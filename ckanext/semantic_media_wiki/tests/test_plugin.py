from datetime import datetime
import importlib.util
import logging
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig
from ckan.config.declaration import Declaration
import pytest
import yaml

from ckanext.semantic_media_wiki.config import (
    LEGACY_MEDIAWIKI_API_ENDPONT,
    MEDIAWIKI_API_ENDPOINT,
    MEDIAWIKI_API_PATH,
    MEDIAWIKI_API_SCHEME,
    MEDIAWIKI_CREDENTIALS_PATH,
    SMW_BASE_URL,
    apply_historical_endpoint_config,
)
from ckanext.semantic_media_wiki.libs.media_wiki import Helper
from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
from ckanext.semantic_media_wiki.machine_plugin import SemanticMediaWikiPlugin
from ckanext.semantic_media_wiki.models.dataset_protocol_link import (
    dataset_protocol_link_table,
)
from ckanext.semantic_media_wiki.models.resource_mediawiki_link import (
    resource_equipment_link_table,
)
from ckanext.semantic_media_wiki.models.resource_sample_link import (
    resource_sample_link_table,
)
from ckanext.semantic_media_wiki.protocol_plugin import ProtocolLinkPlugin
from ckanext.semantic_media_wiki.sample_plugin import SampleLinkPlugin


ASSET_ROOT = Path(__file__).parents[1] / "public" / "statics"
TEMPLATE_ROOT = Path(__file__).parents[1] / "templates"
MIGRATION_ROOT = Path(__file__).parents[1] / "migration"
PLUGIN_TABLES = {
    "machine_link": resource_equipment_link_table,
    "sample_link": resource_sample_link_table,
    "protocol_link": dataset_protocol_link_table,
}


def _load_revision(plugin_name):
    revision_path = next((MIGRATION_ROOT / plugin_name / "versions").glob("*.py"))
    spec = importlib.util.spec_from_file_location(
        f"test_{plugin_name}_migration", revision_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("plugin_name", "model_table"), PLUGIN_TABLES.items())
def test_plugin_migration_matches_model_table(monkeypatch, plugin_name, model_table):
    migration_dir = MIGRATION_ROOT / plugin_name
    assert (migration_dir / "alembic.ini").is_file()

    revision = _load_revision(plugin_name)
    created = {}

    if plugin_name == "machine_link":
        inspector = Mock()
        inspector.has_table.return_value = False
        monkeypatch.setattr(revision.sa, "inspect", lambda bind: inspector)
        monkeypatch.setattr(revision.op, "get_bind", Mock())

    def capture_table(name, *columns):
        created["name"] = name
        created["columns"] = [column.name for column in columns]

    monkeypatch.setattr(revision.op, "create_table", capture_table)
    revision.upgrade()

    assert created["name"] == model_table.name
    assert created["columns"] == list(model_table.columns.keys())


def test_machine_migration_accepts_table_created_by_legacy_plugin(monkeypatch):
    revision = _load_revision("machine_link")
    inspector = Mock()
    inspector.has_table.return_value = True
    monkeypatch.setattr(revision.sa, "inspect", lambda bind: inspector)
    monkeypatch.setattr(revision.op, "get_bind", Mock())
    create_table = Mock()
    monkeypatch.setattr(revision.op, "create_table", create_table)

    revision.upgrade()

    inspector.has_table.assert_called_once_with("resource_equipment_link")
    create_table.assert_not_called()


CUSTOM_CONFIG_KEYS = (
    "ckanext.crc.project.id",
    "ckanext.smw.mediawiki_credentials_path",
    "ckanext.smw.baseurl",
    "ckanext.smw.mediawiki.api.endpoint",
    "ckanext.smw.mediawiki.api.path",
    "ckanext.smw.mediawiki.api.scheme",
    "ckanext.smw.equipment.endpoint",
    "ckanext.smw.machine.endpoint",
    "ckanext.smw.tools.endpoint",
)

CONFIG_DECLARATION = Path(__file__).parents[1] / "config_declaration.yaml"


def _resolve_declared_config(values):
    declaration = Declaration()
    declaration.load_dict(yaml.safe_load(CONFIG_DECLARATION.read_text()))
    config = CKANConfig(values)
    declaration.make_safe(config)
    apply_historical_endpoint_config(config)
    return config


@pytest.mark.parametrize(
    "canonical",
    [
        SMW_BASE_URL,
        MEDIAWIKI_API_ENDPOINT,
        MEDIAWIKI_API_PATH,
        MEDIAWIKI_API_SCHEME,
        MEDIAWIKI_CREDENTIALS_PATH,
    ],
)
def test_config_declaration_preserves_canonical_values(canonical):
    config = _resolve_declared_config({canonical: "canonical-value"})

    assert config[canonical] == "canonical-value"


@pytest.mark.parametrize(
    ("canonical", "legacy"),
    [
        ("ckanext.smw.baseurl", "ckanext.smw.baseUrl"),
        ("ckanext.smw.mediawiki.api.endpoint", "ckanext.smw.mediaWiki.api.endpoint"),
        ("ckanext.smw.mediawiki.api.path", "ckanext.smw.mediaWiki.api.path"),
        ("ckanext.smw.mediawiki.api.scheme", "ckanext.smw.mediaWiki.api.scheme"),
        (
            "ckanext.smw.mediawiki_credentials_path",
            "ckanext.mediaWiki_credentials_path",
        ),
    ],
)
def test_config_declaration_resolves_legacy_keys(caplog, canonical, legacy):
    config = _resolve_declared_config({legacy: "legacy-value"})

    assert config[canonical] == "legacy-value"
    assert (
        f"Config option '{legacy}' is deprecated. Use '{canonical}' instead"
        in caplog.text
    )


def test_historical_endpoint_typo_is_supported(caplog):
    config = _resolve_declared_config({LEGACY_MEDIAWIKI_API_ENDPONT: "old.example"})

    assert config[MEDIAWIKI_API_ENDPOINT] == "old.example"
    assert LEGACY_MEDIAWIKI_API_ENDPONT in caplog.text


@pytest.mark.parametrize(
    "legacy",
    ["ckanext.smw.mediaWiki.api.endpoint", LEGACY_MEDIAWIKI_API_ENDPONT],
)
def test_canonical_endpoint_takes_precedence(caplog, legacy):
    config = _resolve_declared_config(
        {MEDIAWIKI_API_ENDPOINT: "canonical.example", legacy: "legacy.example"}
    )

    assert config[MEDIAWIKI_API_ENDPOINT] == "canonical.example"
    assert legacy not in caplog.text


def test_32_endpoint_takes_precedence_over_historical_typo():
    config = _resolve_declared_config(
        {
            "ckanext.smw.mediaWiki.api.endpoint": "3-2.example",
            LEGACY_MEDIAWIKI_API_ENDPONT: "older.example",
        }
    )

    assert config[MEDIAWIKI_API_ENDPOINT] == "3-2.example"


def test_endpoint_declaration_uses_32_key_as_native_legacy_key():
    declaration = Declaration()
    declaration.load_dict(yaml.safe_load(CONFIG_DECLARATION.read_text()))

    assert (
        declaration.get(MEDIAWIKI_API_ENDPOINT).legacy_key
        == "ckanext.smw.mediaWiki.api.endpoint"
    )


@pytest.mark.parametrize(
    ("environment_key", "canonical"),
    [
        (
            "CKANEXT__SMW__MEDIAWIKI__API__ENDPOINT",
            MEDIAWIKI_API_ENDPOINT,
        ),
        ("CKANEXT__SMW__MEDIAWIKI__API__PATH", MEDIAWIKI_API_PATH),
        (
            "CKANEXT__SMW__MEDIAWIKI__API__SCHEME",
            MEDIAWIKI_API_SCHEME,
        ),
        ("CKANEXT__SMW__BASEURL", SMW_BASE_URL),
        (
            "CKANEXT__SMW__MEDIAWIKI_CREDENTIALS_PATH",
            MEDIAWIKI_CREDENTIALS_PATH,
        ),
    ],
)
def test_normal_ckanext_environment_mapping_matches_declared_key(
    environment_key, canonical
):
    derived_key = environment_key.lower().replace("__", ".")

    assert derived_key == canonical
    assert canonical in _resolve_declared_config({derived_key: "environment-value"})


@pytest.mark.parametrize(
    "key",
    [
        "ckanext.smw.machine.endpoint",
        "ckanext.smw.tools.endpoint",
        "ckanext.smw.equipment.endpoint",
    ],
)
def test_existing_lowercase_endpoint_keys_remain_unchanged(key):
    config = _resolve_declared_config({key: "query.example"})

    assert config[key] == "query.example"


def test_webassets_do_not_reference_obsolete_jquery_ui_bundle():
    for webassets_file in ASSET_ROOT.rglob("webassets.yml"):
        assert "vendor/jquery.ui.core" not in webassets_file.read_text()


def test_webasset_bundles_have_existing_contents():
    for webassets_file in ASSET_ROOT.rglob("webassets.yml"):
        bundles = yaml.safe_load(webassets_file.read_text())
        for name, bundle in bundles.items():
            assert bundle.get("contents"), f"{name} must not be empty"
            for content in bundle["contents"]:
                assert (webassets_file.parent / content).is_file()

    machine_bundles = yaml.safe_load(
        (ASSET_ROOT / "machine_link" / "webassets.yml").read_text()
    )
    assert "machine-image-modal-js" not in machine_bundles


@pytest.mark.parametrize("link_type", ["machine_link", "sample_link"])
def test_resource_templates_only_use_registered_plugin_helper(link_type):
    template = TEMPLATE_ROOT / link_type / "package" / "resource_read.html"
    source = template.read_text()

    assert "h.is_enabled" not in source
    assert 'h.check_plugin_enabled("sfb_layout")' in source
    assert 'h.check_plugin_enabled("crc1153_layout")' in source


@pytest.mark.ckan_config("ckan.plugins", "machine_link sample_link protocol_link")
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
@pytest.mark.usefixtures("with_plugins")
def test_affected_asset_bundle_includes_without_unknown_assets(app, caplog):
    from ckan.lib.webassets_tools import include_asset

    caplog.set_level(logging.ERROR, logger="ckan.lib.webassets_tools")

    with app.flask_app.test_request_context("/"):
        include_asset("ckanext-protocol-link/dataset-protocol-js")

    assert "Trying to include unknown asset" not in caplog.text
    assert "vendor/jquery.ui.core" not in caplog.text


def test_primary_plugin_implements_config_declarations():
    assert plugins.IConfigDeclaration.implemented_by(SemanticMediaWikiPlugin)


@pytest.mark.ckan_config("ckan.plugins", "machine_link sample_link protocol_link")
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
@pytest.mark.usefixtures("with_plugins")
def test_plugins_load_with_all_custom_options_declared(ckan_config, caplog):
    caplog.set_level(logging.WARNING, logger="ckan.common")

    for key in CUSTOM_CONFIG_KEYS:
        assert ckan_config.is_declared(key)
        ckan_config.get(key)

    warning_messages = [
        record.getMessage()
        for phase in ("setup", "call")
        for record in caplog.get_records(phase)
    ]
    for key in CUSTOM_CONFIG_KEYS:
        assert f"Option {key} is not declared" not in warning_messages


def test_api_uses_sfb1153_default_path():
    api = API("", "", "query", "smw.service.tib.eu", "1153")

    assert api.path == "/wiki-sfb1153/"
    assert api.scheme == "https"


def test_api_uses_sfb1368_default_path():
    api = API("", "", "query", "smw.service.tib.eu", "1368")

    assert api.path == "/wiki-sfb1368/"
    assert api.scheme == "https"


def test_api_uses_explicit_path_and_scheme():
    api = API(
        "",
        "",
        "query",
        "wiki.example",
        "custom",
        path="/custom/wiki/",
        scheme="http",
    )

    assert api.path == "/custom/wiki/"
    assert api.scheme == "http"


def test_api_requires_path_for_unknown_project():
    with pytest.raises(ValueError, match="api.path must be configured"):
        API("", "", "query", "wiki.example", "custom")


def test_api_login_uses_sfb1368_endpoint_and_credentials():
    site = Mock()
    with patch("ckanext.semantic_media_wiki.libs.media_wiki_api.Site", return_value=site) as site_cls:
        api = API(
            "user",
            "secret",
            "[[Category:Equipment]]",
            "smw.service.tib.eu",
            "1368",
        )
        assert api.login(api.host, api.path, api.scheme) is True

    site_cls.assert_called_once_with(
        host="smw.service.tib.eu", path="/wiki-sfb1368/", scheme="https"
    )
    site.login.assert_called_once_with(username="user", password="secret")


@pytest.mark.parametrize("config_getter", [Helper.get_api_config, SampleLinkHelper.get_api_config])
def test_api_config_reads_explicit_host_path_and_scheme(monkeypatch, config_getter):
    monkeypatch.setitem(toolkit.config, "ckanext.crc.project.id", "1368")
    monkeypatch.setitem(toolkit.config, MEDIAWIKI_CREDENTIALS_PATH, "/credentials")
    monkeypatch.setitem(toolkit.config, SMW_BASE_URL, "https://wiki.example/")
    monkeypatch.setitem(
        toolkit.config, MEDIAWIKI_API_ENDPOINT, "smw.service.tib.eu"
    )
    monkeypatch.setitem(toolkit.config, MEDIAWIKI_API_PATH, "/custom/wiki/")
    monkeypatch.setitem(toolkit.config, MEDIAWIKI_API_SCHEME, "http")

    config = config_getter()

    assert config[:2] == ["/credentials", "https://wiki.example/"]
    assert config[2] == "smw.service.tib.eu"
    assert config[5:] == ["/custom/wiki/", "http"]


def test_machine_api_receives_connection_settings(monkeypatch):
    monkeypatch.setattr(
        Helper,
        "get_api_config",
        staticmethod(
            lambda: [
                "/credentials",
                "https://smw.service.tib.eu/sfb1368/",
                "smw.service.tib.eu",
                "[[Category:Equipment]]",
                "1368",
                "/wiki-sfb1368/",
                "https",
            ]
        ),
    )
    with patch("builtins.open", mock_open(read_data="username=user\npassword=secret")):
        with patch("ckanext.semantic_media_wiki.libs.media_wiki.API") as api_cls:
            api_cls.return_value.pipeline.return_value = (
                [{"page": "Hand-operated press LP M4S50"}],
                {},
            )
            machines = Helper.get_machines_list()

    api_cls.assert_called_once_with(
        username="user",
        password="secret",
        query="[[Category:Equipment]]",
        host="smw.service.tib.eu",
        target_sfb="1368",
        path="/wiki-sfb1368/",
        scheme="https",
    )
    assert machines[1]["value"] == (
        "https://smw.service.tib.eu/sfb1368/"
        "Hand-operated%20press%20LP%20M4S50"
    )


def test_sample_api_receives_connection_settings(monkeypatch):
    monkeypatch.setattr(
        SampleLinkHelper,
        "get_api_config",
        staticmethod(
            lambda: [
                "/credentials",
                "https://smw.service.tib.eu/sfb1368/",
                "smw.service.tib.eu",
                "[[Category:Samples]]",
                "1368",
                "/wiki-sfb1368/",
                "https",
            ]
        ),
    )
    with patch("builtins.open", mock_open(read_data="username=user\npassword=secret")):
        with patch("ckanext.semantic_media_wiki.libs.sample_link.API") as api_cls:
            api_cls.return_value.pipeline.return_value = (
                [{"page": "Sample A"}],
                {},
            )
            samples = SampleLinkHelper.get_samples_list()

    api_cls.assert_called_once_with(
        username="user",
        password="secret",
        query="[[Category:Samples]]",
        host="smw.service.tib.eu",
        target_sfb="1368",
        sample_query=True,
        path="/wiki-sfb1368/",
        scheme="https",
    )
    assert samples[1]["value"] == "https://smw.service.tib.eu/sfb1368/Sample%20A"


def test_pipeline_paginates_query_and_maps_image_url():
    response = {
        "query": {
            "results": {
                "Machine A": {
                    "fulltext": "Machine A",
                    "printouts": {"Image": [{"fulltext": "File:machine.png"}]},
                }
            }
        }
    }
    api = API("user", "secret", "[[Category:Device]]", "wiki.example", "1153")
    api.login = Mock()
    api.site = Mock()
    api.site.raw_api.return_value = response
    api.mw_getfile_url = Mock(return_value="https://wiki.example/machine.png")

    results, images = api.pipeline(offset=25, limit=50)

    api.site.raw_api.assert_called_once_with(
        "ask", query="[[Category:Device]]|limit=50|offset=25", format="json"
    )
    assert results == [{"page": "Machine A", "Image": "File:machine.png"}]
    assert images == {"Machine A": "https://wiki.example/machine.png"}


def test_sample_pipeline_keeps_results_without_printouts():
    api = API("", "", "[[Category:Samples]]", "wiki.example", "1368", sample_query=True)
    api.login = Mock()
    api.site = Mock()
    api.site.raw_api.return_value = {
        "query": {"results": {"Sample A": {"fulltext": "Sample A", "printouts": {}}}}
    }

    results, images = api.pipeline()

    assert results == [{"page": "Sample A"}]
    assert images == {}


def test_unpack_ask_response_converts_timestamps():
    api = API("", "", "query", "wiki.example", "1368")
    result = api.unpack_ask_response(
        {"fulltext": "Page", "printouts": {"Created": [{"timestamp": "0"}]}}
    )

    assert result == {"page": "Page", "Created": datetime.fromtimestamp(0)}


@pytest.mark.parametrize(
    ("plugin", "route_count"),
    [
        (SemanticMediaWikiPlugin, 6),
        (SampleLinkPlugin, 6),
        (ProtocolLinkPlugin, 5),
    ],
)
def test_plugins_register_expected_routes(plugin, route_count):
    assert len(plugin().get_blueprint().deferred_functions) == route_count
