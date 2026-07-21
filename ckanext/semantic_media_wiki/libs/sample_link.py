# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.semantic_media_wiki.libs.media_wiki_api import API, read_credentials
from urllib import parse
from datetime import datetime as _time
from ckanext.semantic_media_wiki.models.resource_sample_link import ResourceSampleLink
from ckanext.semantic_media_wiki.libs.commons import Common
import logging

log = logging.getLogger(__name__)



class SampleLinkHelper():

    def add_sample_links(request, resources_len, package):
        '''
            Save a sample link in db.

            Arg:
                - request: the request object
                - resources_len: number of data resources in the dataset.
            
            Return:
                - boolean
        '''
        
        try:
            allowed_resource_ids = {res['id'] for res in package.get('resources', [])}
            for i in range(1, resources_len + 1):
                link = request.form.get('sample_link' + str(i))
                if link == '0': # not specified
                    continue            
                sample_name =request.form.get('sample_name_' + str(i))
                if not sample_name or sample_name == '':
                    sample_name = SampleLinkHelper.get_sample_name(link)
                resources_checkbox_list = request.form.getlist('sample_resources_list' + str(i))
                create_at = _time.now()
                updated_at = create_at
                for Id in resources_checkbox_list:
                    if Id not in allowed_resource_ids:
                        continue
                    resource_object = ResourceSampleLink(resource_id=Id, 
                        sample_url=link, 
                        sample_name=sample_name, 
                        create_at=create_at, 
                        updated_at=updated_at
                        )
                    resource_object.save()
        except Exception as exc:
            log.exception("Failed to add sample links: %s", exc)
            return False
            
        return True




    def update_resource_sample(request, resources_len, package):
        '''
            Update a sample link in db.

            Arg:
                - request: the request object
                - resources_len: number of data resources in the dataset.
                - package: target dataset
            
            Return:
                - boolean
        '''
        
        try:
            allowed_resource_ids = {res['id'] for res in package.get('resources', [])}
            already_edited_resources = {}        
            for i in range(1, resources_len + 1):
                link = request.form.get('sample_link' + str(i))
                if link == '0':
                   continue
                sample_name = request.form.get('sample_name_' + str(i))                
                resources_checkbox_list = request.form.getlist('sample_resources_list' + str(i))
                updated_at = _time.now()
                for entry in resources_checkbox_list:
                    Id = entry.split('@@@')[0]
                    if len(entry.split('@@@')) == 2:
                        old_sample_url = entry.split('@@@')[1]
                    else:
                        old_sample_url = ''
                    if Id not in allowed_resource_ids:
                        continue
                    resource_record = ResourceSampleLink(resource_id=Id).get_by_resource_sample(id=Id, sample_url=old_sample_url)
                    if not resource_record:
                        # resource link does not exist --> add a new one
                        create_at = _time.now()
                        updated_at = create_at
                        resource_object = ResourceSampleLink(Id, link, sample_name, create_at, updated_at)
                        resource_object.save()
                        if Id in already_edited_resources.keys():
                            already_edited_resources[Id].append(link)
                        else:
                            already_edited_resources[Id] = [link]
                        continue
                                                                                                                 
                    resource_record.sample_url = link
                    resource_record.sample_name = sample_name
                    resource_record.updated_at = updated_at
                    resource_record.commit()
                    if Id in already_edited_resources.keys():
                        already_edited_resources[Id].append(link)
                    else:
                        already_edited_resources[Id] = [link]
                
                
                for res in package['resources']:
                    resource_objects = ResourceSampleLink(resource_id=res['id']).get_by_resource(id=res['id'])
                    if resource_objects:
                        for record in resource_objects:
                            if record.resource_id not in already_edited_resources.keys():
                                record.delete()
                                record.commit()
                            elif record.sample_url not in already_edited_resources[res['id']]:                                
                                record.delete()
                                record.commit()
            
            Common.set_package_extra(package, "sample", "True")

        except Exception as exc:
            log.exception("Failed to update sample links: %s", exc)
            return False

        return True
    



    def get_sample_name(sample_url):
        '''
            Get a sample name from SMW. 
        '''

        samples = SampleLinkHelper.get_samples_list()
        for sample in samples:
            if sample['value'] == sample_url:
                return sample['text']

        return None



    def get_sample_link(resource_id):
        '''
            Get a sample url from DB for a data resource.
        '''

        res_object = ResourceSampleLink(resource_id=resource_id)
        results = res_object.get_by_resource(id=resource_id)
        urls = {}
        if results:
            for record in results:
                if record.sample_url != '0' and record.sample_name != '':
                    urls[record.sample_name] = record.sample_url
                elif record.sample_url != '0' and record.sample_name == '':
                     urls[record.sample_url] = record.sample_url       
            return urls

        return {}





    def get_samples_list():
        samples = []
        username = None
        password = None
        query = ""
        (
            credentials_path, smw_base_url, api_host, query, sfb,
            api_path, api_scheme, timeout,
        ) = SampleLinkHelper.get_api_config()
        try:
            username, password = read_credentials(credentials_path)
        except (OSError, IndexError, KeyError, ValueError) as exc:
            log.warning("MediaWiki credentials could not be read: %s", exc)
            return []
        
        api_call = API(
            username=username,
            password=password,
            query=query,
            host=api_host,
            target_sfb=sfb,
            sample_query=True,
            path=api_path,
            scheme=api_scheme,
            timeout=timeout,
        )
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
        query = "[[Category:Samples]]"        
        credential_path = toolkit.config.get('ckanext.mediaWiki_credentials_path')
        smw_base_url = toolkit.config.get('ckanext.smw.baseUrl')
        api_host = (
            toolkit.config.get('ckanext.smw.mediaWiki.api.endpoint')
            or toolkit.config.get('ckanext.smw.mediaWiki.api.endpont')
        )
        api_path = toolkit.config.get('ckanext.smw.mediaWiki.path', '/wiki/')
        api_scheme = toolkit.config.get('ckanext.smw.mediaWiki.scheme', 'https')
        timeout = toolkit.config.get('ckanext.smw.mediaWiki.timeout', 30)
        try:
            timeout = float(timeout)
        except (TypeError, ValueError):
            timeout = 30
        sfb = (toolkit.config.get('ckanext.crc.project.id') or '').strip()
        return [credential_path, smw_base_url, api_host, query, sfb, api_path, api_scheme, timeout]



    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False
