# encoding: utf-8

'''
Tests for the ckanext-semantic-media-wiki extension.

'''

import logging
from pathlib import Path

import pytest
from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from os import path
from ckanext.semantic_media_wiki.tests.libs import TestHelper


ASSET_ROOT = Path(__file__).parents[1] / "public" / "statics"


def test_webassets_do_not_reference_obsolete_jquery_ui_bundle():
    for webassets_file in ASSET_ROOT.rglob("webassets.yml"):
        assert "vendor/jquery.ui.core" not in webassets_file.read_text()


@pytest.mark.ckan_config(
    "ckan.plugins", "machine_link sample_link protocol_link"
)
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
@pytest.mark.usefixtures("with_plugins")
def test_affected_asset_bundle_includes_without_unknown_assets(app, caplog):
    from ckan.lib.webassets_tools import include_asset

    caplog.set_level(logging.ERROR, logger="ckan.lib.webassets_tools")

    with app.flask_app.test_request_context("/"):
        include_asset("ckanext-protocol-link/dataset-protocol-js")

    assert "Trying to include unknown asset" not in caplog.text
    assert "vendor/jquery.ui.core" not in caplog.text

@pytest.mark.usefixtures('with_plugins', 'with_request_context')
class TestMediaWiki(object):

    username = None
    password = None
    host_1153 = "service.tib.eu/sfb1153"
    host_1368 = "service.tib.eu/sfb1368"
    query = "[[Category:Equipment]]|?hasManufacturer|?hasModel"  # all Equipments (machines and tools)


    def test_APIcredential_exist_1368(self):
        '''
            The api needs username and password which has to be 
            in /etc/ckan/default/credentials/smw1368.txt
        '''
        assert path.isdir('/etc/ckan/default/credentials/') == True  ## the directory exists
        assert path.isfile('/etc/ckan/default/credentials/smw1368.txt') == True  ## the file exists
        try:
            credentials = open('/etc/ckan/default/credentials/smw1368.txt', 'r').read()
            credentials = credentials.split('\n')
            self.username = credentials[0].split('=')[1]
            self.password = credentials[1].split('=')[1]
           
        except:
            print("The credential file structure is wrong.")
            assert False
        
        assert True
    

    def test_APIcredential_exist_1153(self):
        '''
            The api needs username and password which has to be 
            in /etc/ckan/default/credentials/smw1153.txt
        '''
        assert path.isdir('/etc/ckan/default/credentials/') == True  ## the directory exists
        assert path.isfile('/etc/ckan/default/credentials/smw1153.txt') == True  ## the file exists
        try:
            credentials = open('/etc/ckan/default/credentials/smw1153.txt', 'r').read()
            credentials = credentials.split('\n')
            self.username = credentials[0].split('=')[1]
            self.password = credentials[1].split('=')[1]
           
        except:
            print("The credential file structure is wrong.")
            assert False
        
        assert True



    def test_media_wiki_API_call_1368(self):
        '''
            Test the mediaWiki 1368 API call 
        '''

        try:
            credentials_path, smw_base_url, api_host, query, sfb = TestHelper.get_api_config('1368')
            credentials = open(credentials_path, 'r').read()
            credentials = credentials.split('\n')
            self.username = credentials[0].split('=')[1]
            self.password = credentials[1].split('=')[1]
           
        except:
            print("The credentials do not exist.")
            assert False
        
        try:
            api_call = API(username=self.username, password=self.password, query=query, host=api_host, target_sfb=sfb)
            results, machine_imageUrl = api_call.pipeline()
        except:
            print("API call failed.")
            assert False
        
        if not results or len(results) == 0:
            print("API returns nothing.")
            assert False

        assert True
    

    def test_media_wiki_API_call_1153(self):
        '''
            Test the mediaWiki 1153 API call 
        '''

        try:
            credentials_path, smw_base_url, api_host, query, sfb = TestHelper.get_api_config('1153')
            credentials = open(credentials_path, 'r').read()
            credentials = credentials.split('\n')
            self.username = credentials[0].split('=')[1]
            self.password = credentials[1].split('=')[1]
           
        except:
            print("The credentials do not exist.")
            assert False
        
        try:
            api_call = API(username=self.username, password=self.password, query=query, host=api_host, target_sfb=sfb)
            results, machine_imageUrl = api_call.pipeline()
        except:
            print("API call failed.")
            assert False
        
        if not results or len(results) == 0:
            print("API returns nothing.")
            assert False

        assert True

