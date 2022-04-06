# encoding: utf-8

from sqlalchemy.sql.expression import false, true
from ckanext.semantic_media_wiki.models.resource_mediawiki_link import ResourceEquipmentLink
from datetime import datetime as _time
from ckanext.semantic_media_wiki.libs.media_wiki_api import API
from urllib import parse
import ckan.plugins.toolkit as toolkit


class Helper():

    def check_access_edit_package(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_update', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            return False


    def add_machine_links(request, resources_len):
        
        try:
            for i in range(1, resources_len + 1):    
                link = request.form.get('machine_link' + str(i))
                if link == '0': # not specified
                    continue            
                machine_name =request.form.get('machine_name_' + str(i))
                if not machine_name or machine_name == '':
                    machine_name = Helper.get_machine_name(link)
                resources_checkbox_list = request.form.getlist('machine_resources_list' + str(i))
                create_at = _time.now()
                updated_at = create_at
                for Id in resources_checkbox_list:
                    resource_object = ResourceEquipmentLink(Id, link, machine_name, create_at, updated_at)
                    resource_object.save()
        except:
            return false
            
        return true

    def update_resource_machine(request, resources_len, package):
        
        try:
            already_edited_resources = {}        
            for i in range(1, resources_len + 1):
                link = request.form.get('machine_link' + str(i))
                if link == '0':
                    machine_name = None
                machine_name = request.form.get('machine_name_' + str(i))
                if not machine_name or machine_name == '':
                    machine_name = Helper.get_machine_name(link)
                resources_checkbox_list = request.form.getlist('machine_resources_list' + str(i))
                updated_at = _time.now()
                for entry in resources_checkbox_list:
                    Id = entry.split('@@@')[0]
                    if len(entry.split('@@@')) == 2:
                        old_machine_url = entry.split('@@@')[1]
                    else:
                        old_machine_url = ''
                    resource_record = ResourceEquipmentLink(resource_id=Id).get_by_resource_machine(id=Id, machine_url=old_machine_url)
                    if not resource_record:
                        # resource link does not exist --> add a new one
                        create_at = _time.now()
                        updated_at = create_at
                        resource_object = ResourceEquipmentLink(Id, link, machine_name, create_at, updated_at)
                        resource_object.save()
                        if Id in already_edited_resources.keys():
                            already_edited_resources[Id].append(link)
                        else:
                            already_edited_resources[Id] = [link]
                        continue
                                                                                                                 
                    resource_record.url = link
                    resource_record.link_name = machine_name
                    resource_record.updated_at = updated_at
                    resource_record.commit()
                    if Id in already_edited_resources.keys():
                        already_edited_resources[Id].append(link)
                    else:
                        already_edited_resources[Id] = [link]
                
                
                for res in package['resources']:
                    resource_objects = ResourceEquipmentLink(resource_id=res['id']).get_by_resource(id=res['id'])
                    if resource_objects:
                        for record in resource_objects:
                            if record.resource_id not in already_edited_resources.keys():
                                record.delete()
                                record.commit()
                            elif record.url not in already_edited_resources[res['id']]:                                
                                record.delete()
                                record.commit() 

        except:
            # raise 
            return False

        return True

    
    def get_machine_link(resource_id):
        res_object = ResourceEquipmentLink(resource_id=resource_id)
        results = res_object.get_by_resource(id=resource_id)
        urls = {}
        if results:
            for record in results:
                if record.url != '0' and record.link_name != '':
                    urls[record.link_name] = record.url
                elif record.url != '0' and record.link_name == '':
                     urls[record.url] = record.url       
            return urls

        return {}
    

    def get_machines_list():
        machines_list = []
        username = None
        password = None
        query = ""
        credentials_path, smw_base_url, api_host, query, sfb = Helper.get_api_config()          
        try:
            credentials = open(credentials_path, 'r').read()
            credentials = credentials.split('\n')
            username = credentials[0].split('=')[1]
            password = credentials[1].split('=')[1]
           
        except:
            return [[], []]
        
        api_call = API(username=username, password=password, query=query, host=api_host, target_sfb=sfb)
        results, machine_imageUrl = api_call.pipeline()
        if results and len(results) > 0:
            temp = {}
            temp['value'] = '0'
            temp['text'] = 'None selected'
            machines_list.append(temp)
            for machine in results:
                temp = {}
                temp['value'] = smw_base_url + parse.quote(machine['page'])
                temp['text'] = machine['page']
                if machine_imageUrl.get( machine['page']):
                    temp['image'] = machine_imageUrl.get( machine['page'])
                else:
                    temp['image'] = ''
                machines_list.append(temp)
                        
            return [machines_list, machine_imageUrl]
        
        return [[], []]
    

    def get_machine_name(machine_url):
        machines, images = Helper.get_machines_list()
        for machine in machines:
            if machine['value'] == machine_url:
                return machine['text']

        return None
    

    def get_api_config():
        credential_path = '/etc/ckan/default/credentials/smw1153.txt'
        smw_base_url = "https://service.tib.eu/sfb1153/wiki/"
        api_host = "service.tib.eu/sfb1153"
        query = "[[Category:Device]]|?HasManufacturer|?HasImage|?HasType"
        sfb = "1153"
        ckan_root_path = toolkit.config.get('ckan.root_path')
        if  ckan_root_path and 'sfb1368/ckan' in ckan_root_path:
            credential_path = '/etc/ckan/default/credentials/smw1368.txt'
            smw_base_url = "https://service.tib.eu/sfb1368/wiki/"
            api_host = "service.tib.eu/sfb1368"
            query = "[[Category:Equipment]]|?hasManufacturer|?hasModel|?depiction"
            sfb = "1368"

        return [credential_path, smw_base_url, api_host, query, sfb]
    

    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False
    



