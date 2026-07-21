# encoding: utf-8

from ckanext.semantic_media_wiki.models.resource_mediawiki_link import ResourceEquipmentLink
from datetime import datetime as _time
from ckanext.semantic_media_wiki.libs.media_wiki_api import API, read_credentials
from urllib import parse
import ckan.plugins.toolkit as toolkit
from ckanext.semantic_media_wiki.libs.commons import Common
from flask import redirect
import ckan.lib.helpers as h
import logging

log = logging.getLogger(__name__)


class Helper():


    def add_machine_links(request, resources_len, package):
        
        try:
            allowed_resource_ids = {res['id'] for res in package.get('resources', [])}
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
                    if Id not in allowed_resource_ids:
                        continue
                    resource_object = ResourceEquipmentLink(Id, link, machine_name, create_at, updated_at)
                    resource_object.save()
        except Exception as exc:
            log.exception("Failed to add machine links: %s", exc)
            return False
            
        return True

    def update_resource_machine(request, resources_len, package):
        
        try:
            already_edited_resources = {}        
            for i in range(1, resources_len + 1):
                link = request.form.get('machine_link' + str(i))
                if link == '0':
                    continue
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
                
                Common.set_package_extra(package, "machine", "True")

        except Exception as exc:
            log.exception("Failed to update machine links: %s", exc)
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
        (
            credentials_path, smw_base_url, api_host, query, sfb,
            api_path, api_scheme, timeout,
        ) = Helper.get_api_config()
        try:
            username, password = read_credentials(credentials_path)
        except (OSError, IndexError, KeyError, ValueError) as exc:
            log.warning("MediaWiki credentials could not be read: %s", exc)
            return [[], []]
        
        api_call = API(
            username=username,
            password=password,
            query=query,
            host=api_host,
            target_sfb=sfb,
            path=api_path,
            scheme=api_scheme,
            timeout=timeout,
        )
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
                        
            return machines_list
        
        return []
    

    def get_machine_name(machine_url):
        machines = Helper.get_machines_list()
        for machine in machines:
            if machine['value'] == machine_url:
                return machine['text']

        return None
    

    def get_api_config():
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
        query = ""
        if  sfb == "1368":
            query = "[[Category:Equipment]]|?hasManufacturer|?hasModel|?depiction"
        else:
            query = "[[Category:Device]]|?HasManufacturer|?HasImage|?HasType"

        return [credential_path, smw_base_url, api_host, query, sfb, api_path, api_scheme, timeout]
    


    @staticmethod
    def get_next_step_redirect(package_name):
        if Common.check_plugin_enabled('sample_link'):
            return redirect(h.url_for('sample_link.add_samples_view', id=str(package_name) ,  _external=True))     
        return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
    
    

