"""Tests for the Semantic MediaWiki API client."""

from unittest.mock import Mock, patch

import pytest

from ckanext.semantic_media_wiki.libs.media_wiki_api import API


@pytest.mark.usefixtures("with_plugins", "with_request_context")
class TestMediaWiki:
    def test_login_uses_credentials(self):
        site = Mock()

        with patch(
            "ckanext.semantic_media_wiki.libs.media_wiki_api.Site",
            return_value=site,
        ) as site_class:
            api = API("username", "password", "query", "example.org", "1153")
            assert api.login("example.org", "/wiki/", "https") is True

        site_class.assert_called_once_with(
            host="example.org", path="/wiki/", scheme="https"
        )
        site.login.assert_called_once_with(username="username", password="password")
        assert api.site is site

    def test_login_without_credentials_is_anonymous(self):
        site = Mock()

        with patch(
            "ckanext.semantic_media_wiki.libs.media_wiki_api.Site",
            return_value=site,
        ):
            api = API(None, None, "query", "example.org", "1368")
            api.login("example.org", "/wiki/", "https")

        site.login.assert_not_called()

    def test_pipeline_processes_results_and_image(self):
        api = API(
            "username", "password", "[[Category:Device]]", "example.org", "1153"
        )
        api.login = Mock()
        api.mw_getfile_url = Mock(return_value="https://example.org/device.jpg")
        api.site = Mock()
        api.site.raw_api.return_value = {
            "query": {
                "results": {
                    "Device A": {
                        "fulltext": "Device A",
                        "printouts": {
                            "HasManufacturer": ["ACME"],
                            "Image": [{"fulltext": "File:device.jpg"}],
                        },
                    }
                }
            }
        }

        results, image_urls = api.pipeline(offset=20, limit=10)

        api.login.assert_called_once_with(api.host, api.path, api.scheme)
        api.site.raw_api.assert_called_once_with(
            "ask",
            query="[[Category:Device]]|limit=10|offset=20",
            format="json",
        )
        assert results == [
            {
                "page": "Device A",
                "HasManufacturer": "ACME",
                "Image": "File:device.jpg",
            }
        ]
        assert image_urls == {"Device A": "https://example.org/device.jpg"}
        api.mw_getfile_url.assert_called_once_with(filepage="File:device.jpg")

    def test_pipeline_returns_empty_results_when_api_call_fails(self):
        api = API(None, None, "query", "example.org", "1368")
        api.login = Mock()
        api.site = Mock()
        api.site.raw_api.side_effect = RuntimeError("service unavailable")

        assert api.pipeline() == [[], {}]
