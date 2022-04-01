# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from urllib import parse


class SampleLinkHelper():

    def check_access_edit_package(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_update', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            return False
    


    def get_samples_list():
        samples = []
        username = None
        password = None
        query = ""
        credentials_path, smw_base_url, api_host, query, sfb = SampleLinkHelper.get_api_config()          
        try:
            credentials = open(credentials_path, 'r').read()
            credentials = credentials.split('\n')
            username = credentials[0].split('=')[1]
            password = credentials[1].split('=')[1]
           
        except:
            return [[], []]
        
        api_call = API(username=username, password=password, query=query, host=api_host, target_sfb=sfb)
        results, _ = api_call.pipeline()
        if results and len(results) > 0:
            temp = {}
            temp['value'] = '0'
            temp['text'] = 'None selected'
            samples.append(temp)
            for samp in results:
                temp = {}
                temp['value'] = smw_base_url + parse.quote(samp['page'])
                temp['text'] = samp['page']
                samples.append(temp)
                        
            return samples
        
        return []



    @staticmethod
    def get_api_config():
        credential_path = '/etc/ckan/default/credentials/smw1153.txt'
        smw_base_url = "https://service.tib.eu/sfb1153/wiki/"
        api_host = "service.tib.eu/sfb1153"
        query = "[[Category:Samples]]"
        sfb = "1153"
        ckan_root_path = toolkit.config.get('ckan.root_path')
        if  ckan_root_path and 'sfb1368/ckan' in ckan_root_path:
            credential_path = '/etc/ckan/default/credentials/smw1368.txt'
            smw_base_url = "https://service.tib.eu/sfb1368/wiki/"
            api_host = "service.tib.eu/sfb1368"
            query = "[[Category:Samples]]"
            sfb = "1368"

        return [credential_path, smw_base_url, api_host, query, sfb]