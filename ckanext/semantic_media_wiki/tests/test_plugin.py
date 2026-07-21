# encoding: utf-8

import json

import pytest
from ckan.model import meta
import ckan.plugins as plugins
from ckan.tests import factories

from ckanext.semantic_media_wiki.libs import media_wiki_api
from ckanext.semantic_media_wiki.libs.media_wiki import Helper
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
from ckanext.semantic_media_wiki.models.dataset_protocol_link import (
    DatasetProtocolLink,
    dataset_protocol_link_table,
)
from ckanext.semantic_media_wiki.models.resource_mediawiki_link import (
    ResourceEquipmentLink,
    resource_equipment_link_table,
)
from ckanext.semantic_media_wiki.models.resource_sample_link import (
    ResourceSampleLink,
    resource_sample_link_table,
)


PLUGIN_NAMES = ("machine_link", "sample_link", "protocol_link")
EXTENSION_TABLES = (
    resource_equipment_link_table,
    resource_sample_link_table,
    dataset_protocol_link_table,
)


@pytest.fixture
def extension_tables(clean_db):
    meta.metadata.create_all(bind=meta.engine, tables=EXTENSION_TABLES)
    for model in (ResourceEquipmentLink, ResourceSampleLink, DatasetProtocolLink):
        meta.Session.query(model).delete()
    meta.Session.commit()
    yield
    for model in (ResourceEquipmentLink, ResourceSampleLink, DatasetProtocolLink):
        meta.Session.query(model).delete()
    meta.Session.commit()


@pytest.fixture
def sysadmin_env():
    user = factories.Sysadmin()
    return {"REMOTE_USER": str(user["name"])}


@pytest.fixture
def dataset_with_resource():
    dataset = factories.Dataset()
    resource = factories.Resource(package_id=dataset["id"], name="resource-one")
    dataset["resources"] = [resource]
    return dataset, resource


@pytest.fixture
def mediawiki_config(ckan_config, tmp_path):
    credentials = tmp_path / "smw.txt"
    credentials.write_text("username=wiki-user\npassword=wiki-password\n")
    ckan_config["ckanext.mediaWiki_credentials_path"] = str(credentials)
    ckan_config["ckanext.smw.baseUrl"] = "https://wiki.example.test/sfb1153/wiki/"
    ckan_config["ckanext.smw.mediaWiki.api.endpoint"] = "wiki.example.test"
    ckan_config["ckanext.smw.mediaWiki.path"] = "/sfb1153/wiki/"
    ckan_config["ckanext.smw.mediaWiki.scheme"] = "https"
    ckan_config["ckanext.smw.mediaWiki.timeout"] = "7"
    ckan_config["ckanext.crc.project.id"] = "1153"
    ckan_config["ckanext.smw.machine.endpoint"] = "https://wiki.example.test/new-machine"
    ckan_config["ckanext.smw.tools.endpoint"] = "https://wiki.example.test/new-tool"
    ckan_config["ckanext.smw.equipment.endpoint"] = "https://wiki.example.test/new-equipment"
    return credentials


@pytest.mark.usefixtures("with_plugins")
class TestPluginLoading:
    def test_all_plugins_load_together(self):
        assert all(plugins.plugin_loaded(name) for name in PLUGIN_NAMES)

    def test_blueprint_routes_are_registered(self, app):
        rules = {rule.endpoint: rule.rule for rule in app.flask_app.url_map.iter_rules()}

        assert rules["machine_link.machines_view"] == "/smw/machines_view/<id>"
        assert rules["machine_link.save_machines"] == "/smw/save_machines"
        assert rules["machine_link.edit_machines_view"] == "/smw/edit_machines_view/<id>"
        assert rules["machine_link.get_machine_link"] == "/smw/get_machine_link/<id>"
        assert rules["machine_link.get_resource_machine"] == "/smw/get_resource_machine/<id>"
        assert rules["machine_link.edit_save"] == "/smw/edit_save"
        assert rules["sample_link.add_samples_view"] == "/smw/add_samples_view/<id>"
        assert rules["sample_link.save_samples"] == "/smw/save_samples"
        assert rules["sample_link.get_samples_link"] == "/smw/get_samples_link/<id>"
        assert rules["sample_link.get_resource_sample"] == "/smw/get_resource_sample/<id>"
        assert rules["sample_link.edit_samples_view"] == "/smw/edit_samples_view/<id>"
        assert rules["sample_link.edit_save_samples"] == "/smw/edit_save_samples"
        assert rules["protocol_link.protocol_index"] == "/smw/protocol_index"
        assert rules["protocol_link.save_protocol"] == "/smw/save_protocol"
        assert rules["protocol_link.get_protocol"] == "/smw/get_protocol/<dataset_id>"
        assert rules["protocol_link.edit_protocol_view"] == "/smw/edit_protocol_view/<dataset_id>"
        assert rules["protocol_link.unlink_protocol"] == "/smw/unlink_protocol"


@pytest.mark.usefixtures("with_plugins", "extension_tables", "mediawiki_config")
class TestMediaWikiApi:
    def test_mediawiki_api_uses_config_values_and_parses_results(self, monkeypatch):
        calls = {}

        class FakeImage:
            imageinfo = {"url": "https://wiki.example.test/files/machine.png"}

        class FakeSite:
            def __init__(self, host, path, scheme, reqs):
                calls["site"] = {
                    "host": host,
                    "path": path,
                    "scheme": scheme,
                    "timeout": reqs["timeout"],
                }
                self.images = {"machine.png": FakeImage()}

            def login(self, username, password):
                calls["login"] = {"username": username, "password": password}

            def raw_api(self, action, **kwargs):
                calls["raw_api"] = {"action": action, "kwargs": kwargs}
                return {
                    "query": {
                        "results": {
                            "Machine A": {
                                "fulltext": "Machine A",
                                "printouts": {
                                    "Image": [{"fulltext": "File:machine.png"}],
                                    "HasManufacturer": ["ACME"],
                                },
                            }
                        }
                    }
                }

        monkeypatch.setattr(media_wiki_api, "Site", FakeSite)

        config = Helper.get_api_config()
        api = media_wiki_api.API(
            username="wiki-user",
            password="wiki-password",
            query=config[3],
            host=config[2],
            target_sfb=config[4],
            path=config[5],
            scheme=config[6],
            timeout=config[7],
        )

        results, image_urls = api.pipeline(offset=10, limit=25)

        assert calls["site"] == {
            "host": "wiki.example.test",
            "path": "/sfb1153/wiki/",
            "scheme": "https",
            "timeout": 7.0,
        }
        assert calls["login"] == {"username": "wiki-user", "password": "wiki-password"}
        assert calls["raw_api"]["action"] == "ask"
        assert calls["raw_api"]["kwargs"]["query"].endswith("|limit=25|offset=10")
        assert results == [
            {"page": "Machine A", "Image": "File:machine.png", "HasManufacturer": "ACME"}
        ]
        assert image_urls == {"Machine A": "https://wiki.example.test/files/machine.png"}

    def test_mediawiki_timeout_returns_safe_empty_result(self, monkeypatch):
        import requests

        class TimeoutSite:
            def __init__(self, *args, **kwargs):
                self.images = {}

            def login(self, username, password):
                return None

            def raw_api(self, *args, **kwargs):
                raise requests.exceptions.Timeout("timed out")

        monkeypatch.setattr(media_wiki_api, "Site", TimeoutSite)
        api = media_wiki_api.API(
            username="wiki-user",
            password="wiki-password",
            query="[[Category:Device]]",
            host="wiki.example.test",
            target_sfb="1153",
            path="/wiki/",
            timeout=1,
        )

        assert api.pipeline() == [[], {}]

    def test_sample_config_is_ckan_configuration_driven(self):
        assert SampleLinkHelper.get_api_config() == [
            str(Helper.get_api_config()[0]),
            "https://wiki.example.test/sfb1153/wiki/",
            "wiki.example.test",
            "[[Category:Samples]]",
            "1153",
            "/sfb1153/wiki/",
            "https",
            7.0,
        ]


@pytest.mark.usefixtures("with_plugins", "extension_tables", "mediawiki_config")
class TestRoutesAndPersistence:
    def test_important_get_routes_render_or_return_safe_data(
            self, app, sysadmin_env, dataset_with_resource, monkeypatch):
        dataset, resource = dataset_with_resource
        monkeypatch.setattr(Helper, "get_machines_list", lambda: [{"value": "0", "text": "None selected", "image": ""}])
        monkeypatch.setattr(SampleLinkHelper, "get_samples_list", lambda: [{"value": "0", "text": "None selected"}])

        assert app.get("/smw/protocol_index").body == "0"
        assert app.get("/smw/machines_view/{0}".format(dataset["name"]), extra_environ=sysadmin_env).status_code == 200
        assert app.get("/smw/edit_machines_view/{0}".format(dataset["name"]), extra_environ=sysadmin_env).status_code == 200
        assert app.get("/smw/add_samples_view/{0}".format(dataset["name"]), extra_environ=sysadmin_env).status_code == 200
        assert app.get("/smw/edit_samples_view/{0}".format(dataset["name"]), extra_environ=sysadmin_env).status_code == 200
        assert app.get("/smw/edit_protocol_view/{0}".format(dataset["id"]), extra_environ=sysadmin_env).status_code == 200
        assert app.get("/smw/get_resource_machine/{0}".format(resource["id"])).body == "0"
        assert app.get("/smw/get_resource_sample/{0}".format(resource["id"])).body == "0"
        assert json.loads(app.get("/smw/get_protocol/{0}".format(dataset["id"])).body) == {}

    def test_save_and_read_machine_links(self, app, sysadmin_env, dataset_with_resource, monkeypatch):
        dataset, resource = dataset_with_resource
        monkeypatch.setattr(Helper, "get_machine_name", lambda url: "Machine A")

        app.post(
            "/smw/save_machines",
            data={
                "package": dataset["name"],
                "machine_count": "1",
                "machine_link1": "https://wiki.example.test/Machine_A",
                "machine_resources_list1": resource["id"],
                "save_btn": "finish_machine",
            },
            extra_environ=sysadmin_env,
            follow_redirects=False,
            status=302,
        )

        assert Helper.get_machine_link(resource["id"]) == {
            "Machine A": "https://wiki.example.test/Machine_A"
        }
        assert json.loads(app.get("/smw/get_resource_machine/{0}".format(resource["id"])).body) == {
            "Machine A": "https://wiki.example.test/Machine_A"
        }

    def test_save_and_edit_sample_links(self, app, sysadmin_env, dataset_with_resource, monkeypatch):
        dataset, resource = dataset_with_resource
        monkeypatch.setattr(SampleLinkHelper, "get_sample_name", lambda url: "Sample A")

        app.post(
            "/smw/save_samples",
            data={
                "package": dataset["name"],
                "sample_count": "1",
                "sample_link1": "https://wiki.example.test/Sample_A",
                "sample_resources_list1": resource["id"],
                "save_btn": "finish_machine",
            },
            extra_environ=sysadmin_env,
            follow_redirects=False,
            status=302,
        )
        assert SampleLinkHelper.get_sample_link(resource["id"]) == {
            "Sample A": "https://wiki.example.test/Sample_A"
        }

        app.post(
            "/smw/edit_save_samples",
            data={
                "package": dataset["name"],
                "sample_count": "1",
                "sample_link1": "https://wiki.example.test/Sample_B",
                "sample_name_1": "Sample B",
                "sample_resources_list1": "{0}@@@https://wiki.example.test/Sample_A".format(resource["id"]),
                "save_btn": "update_sample",
            },
            extra_environ=sysadmin_env,
            follow_redirects=False,
            status=302,
        )

        assert SampleLinkHelper.get_sample_link(resource["id"]) == {
            "Sample B": "https://wiki.example.test/Sample_B"
        }

    def test_protocol_save_read_and_unlink(self, app, sysadmin_env, dataset_with_resource):
        dataset, _ = dataset_with_resource

        app.post(
            "/smw/save_protocol",
            data={
                "dataset_id": dataset["id"],
                "protocol_url": "https://wiki.example.test/Protocol_A",
                "protocol_name": "Protocol A",
            },
            extra_environ=sysadmin_env,
            follow_redirects=False,
            status=302,
        )

        assert json.loads(app.get("/smw/get_protocol/{0}".format(dataset["id"])).body) == {
            "Protocol A": "https://wiki.example.test/Protocol_A"
        }

        app.post(
            "/smw/unlink_protocol",
            data={"dataset_id": dataset["id"], "protocol_list": "Protocol A"},
            extra_environ=sysadmin_env,
            follow_redirects=False,
            status=302,
        )

        assert json.loads(app.get("/smw/get_protocol/{0}".format(dataset["id"])).body) == {}

    @pytest.mark.parametrize("url", ["/smw/save_machines", "/smw/save_samples", "/smw/save_protocol", "/smw/unlink_protocol"])
    def test_anonymous_post_requests_are_rejected(self, app, dataset_with_resource, url):
        dataset, _ = dataset_with_resource
        app.post(
            url,
            data={
                "package": dataset["name"],
                "dataset_id": dataset["id"],
                "machine_count": "1",
                "sample_count": "1",
                "save_btn": "finish_machine",
                "protocol_name": "Protocol A",
                "protocol_url": "https://wiki.example.test/Protocol_A",
            },
            status=403,
        )

    @pytest.mark.parametrize("url", ["/smw/save_machines", "/smw/save_samples"])
    def test_malformed_save_requests_return_safe_errors(self, app, sysadmin_env, dataset_with_resource, url):
        dataset, _ = dataset_with_resource
        app.post(
            url,
            data={"package": dataset["name"], "machine_count": "not-int", "sample_count": "not-int"},
            extra_environ=sysadmin_env,
            status=400,
        )

    def test_invalid_dataset_requests_return_safe_errors(self, app, sysadmin_env):
        app.post(
            "/smw/save_machines",
            data={"package": "missing-dataset", "machine_count": "1", "save_btn": "finish_machine"},
            extra_environ=sysadmin_env,
            status=400,
        )
        assert json.loads(app.get("/smw/get_protocol/missing-dataset").body) == {}
