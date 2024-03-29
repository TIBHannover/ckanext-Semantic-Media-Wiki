# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template, request, redirect
from ckanext.semantic_media_wiki.libs.media_wiki import Helper
from sqlalchemy.sql.expression import false
import json
import ckan.lib.helpers as h
from ckanext.semantic_media_wiki.libs.commons import Common


class MediaWikiController():

    def render_add_machines_view(id):
        Common.abort_if_dataset_editing_not_permit(id)
        package = toolkit.get_action('package_show')({}, {'name_or_id': id})        
        machines = Helper.get_machines_list()
        return render_template('add_machines.html', 
            pkg_dict=package, 
            machines_list=machines,
            custom_stage=True            
            )
    


    def save_machines():
        package_name = request.form.get('package')
        machine_count = request.form.get('machine_count')
        if package_name == None:
            return toolkit.abort(403, "bad request")        
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})
            Common.abort_if_dataset_editing_not_permit(package['id'])               
            action = request.form.get('save_btn')
            if action == 'go-dataset-veiw': # "I will add it later" button
                return Helper.get_next_step_redirect(package_name)
            
            if action == 'finish_machine':
                Helper.add_machine_links(request, int(machine_count))                
                return Helper.get_next_step_redirect(package_name)                                        
        except:
            return toolkit.abort(500, "Server Issue") 
               
        return toolkit.abort(403, "bad request")
    


    def edit_machines_view(id):
        Common.abort_if_dataset_editing_not_permit(id)
        package = toolkit.get_action('package_show')({}, {'name_or_id': id})
        machines = Helper.get_machines_list()
        resource_machine_data = {}
        machine_link_name = {}
        for resource in package['resources']:
            urls = Helper.get_machine_link(resource['id'])
            for name, url in urls.items(): 
                if url not in resource_machine_data.keys():
                    resource_machine_data[url] = [resource['id']]
                    machine_link_name[url] = name
                else:
                    resource_machine_data[url].append(resource['id'])

        return render_template('edit_machines.html', 
            pkg_dict=package, 
            machines_list=machines, 
            resource_data=resource_machine_data,            
            machines_count=len(resource_machine_data.keys()),
            machine_link_name=machine_link_name
            )
    


    def edit_save():
        package_name = request.form.get('package')
        machine_count = request.form.get('machine_count')  
        package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})
        Common.abort_if_dataset_editing_not_permit(package['id'])
        action = request.form.get('save_btn')
        if action == 'go-dataset-veiw': # cancel button
            return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
        
        if action == 'update_machine':
            result = Helper.update_resource_machine(request, int(machine_count), package)
            if result:
                return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))    

            return toolkit.abort(500, "Server issue")    

        return toolkit.abort(403, "bad request")
    
    

    def get_machine_link(id):
        if not toolkit.g.user: 
            return toolkit.abort(403, "You are not authorized to access this function" )
                
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': id})
            machine_links = []
            results = []
            for res in package['resources']:
                machien_urls = Helper.get_machine_link(res['id'])
                if len(machien_urls.keys()) == 0:
                    continue
                for name, link in machien_urls.items():
                    if link not in machine_links:
                        machine_links.append(link)
                        eq_name = name
                        if name == '':
                            eq_name = "Link to the Equipment"
                        temp =  ['', '']
                        temp[0] = link
                        temp[1] = eq_name
                        results.append(temp)
        except:
            # raise
            return toolkit.abort(403, "bad request")

        if len(results) == 0:
            return '0'
        return json.dumps(results)
    


    def get_resource_machine(id):
        urls = Helper.get_machine_link(id)
        if len(urls.keys()) == 0:
            return '0'
        return json.dumps(urls)
    


    def get_smw_endpoints():
        project_id = toolkit.config.get('ckanext.crc.project.id')
        if project_id == "1368":
            machine_endpoint = toolkit.config.get('ckanext.smw.equipment.endpoint')
            tools_endpoint = None
            return [project_id, machine_endpoint, tools_endpoint]
        
        machine_endpoint = toolkit.config.get('ckanext.smw.machine.endpoint')
        tools_endpoint = toolkit.config.get('ckanext.smw.tools.endpoint')
        return [project_id, machine_endpoint, tools_endpoint]
        
    



