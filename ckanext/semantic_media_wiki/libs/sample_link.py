# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from urllib import parse
from datetime import datetime as _time
from ckanext.semantic_media_wiki.models.resource_sample_link import ResourceSampleLink



class SampleLinkHelper():

    def add_sample_links(request, resources_len):
        '''
            Save a sample link in db.

            Arg:
                - request: the request object
                - resources_len: number of data resources in the dataset.
            
            Return:
                - boolean
        '''
        
        try:
            for i in range(1, resources_len):    
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
                    resource_object = ResourceSampleLink(resource_id=Id, 
                        sample_url=link, 
                        sample_name=sample_name, 
                        create_at=create_at, 
                        updated_at=updated_at
                        )
                    resource_object.save()
        except:
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
            already_edited_resources = {}        
            for i in range(1, resources_len):
                link = request.form.get('sample_link' + str(i))
                if link == '0':
                   continue
                sample_name = request.form.get('sample_name_' + str(i))
                if not sample_name or sample_name != 'noPicked':
                    sample_name = SampleLinkHelper.get_sample_name(link)
                resources_checkbox_list = request.form.getlist('sample_resources_list' + str(i))
                updated_at = _time.now()
                for entry in resources_checkbox_list:
                    Id = entry.split('@@@')[0]
                    if len(entry.split('@@@')) == 2:
                        old_sample_url = entry.split('@@@')[1]
                    else:
                        old_sample_url = ''
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
            
            package_extras = []
            package_extras.append({"key": "sample", "value": "True"})
            package['extras'] = package_extras           
            toolkit.get_action('package_update')({},package)

        except:
            # raise 
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
        credentials_path, smw_base_url, api_host, query, sfb = SampleLinkHelper.get_api_config()          
        try:
            credentials = open(credentials_path, 'r').read()
            credentials = credentials.split('\n')
            username = credentials[0].split('=')[1]
            password = credentials[1].split('=')[1]
           
        except:
            return []
        
        api_call = API(username=username, password=password, query=query, host=api_host, target_sfb=sfb, sample_query=True)
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



    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False