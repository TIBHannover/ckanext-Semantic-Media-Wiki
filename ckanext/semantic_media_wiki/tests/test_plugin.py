import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from ckanext.semantic_media_wiki.machine_plugin import SemanticMediaWikiPlugin
from ckanext.semantic_media_wiki.protocol_plugin import ProtocolLinkPlugin
from ckanext.semantic_media_wiki.sample_plugin import SampleLinkPlugin


ASSET_ROOT = Path(__file__).parents[1] / "public" / "statics"


def test_webassets_do_not_reference_obsolete_jquery_ui_bundle():
    for webassets_file in ASSET_ROOT.rglob("webassets.yml"):
        assert "vendor/jquery.ui.core" not in webassets_file.read_text()


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


def test_api_login_uses_configured_endpoint_and_credentials():
    site = Mock()
    with patch("ckanext.semantic_media_wiki.libs.media_wiki_api.Site", return_value=site) as site_cls:
        api = API("user", "secret", "[[Category:Device]]", "wiki.example", "1153")
        assert api.login("wiki.example", "/wiki/", "https") is True

    site_cls.assert_called_once_with(host="wiki.example", path="/wiki/", scheme="https")
    site.login.assert_called_once_with(username="user", password="secret")


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
