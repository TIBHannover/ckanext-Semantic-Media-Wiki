# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template, request, redirect
from ckanext.semantic_media_wiki.libs.media_wiki import Helper
from sqlalchemy.sql.expression import false
import json
import ckan.lib.helpers as h



class MediaWikiController():

    def machines_view(id):
        if not Helper.check_access_edit_package(id):
            toolkit.abort(403, 'You are not authorized to access this function')

        package = toolkit.get_action('package_show')({}, {'name_or_id': id})
        stages = ['complete', 'complete','complete', 'active']
        machines, machine_imageUrl = Helper.get_machines_list()
        return render_template('add_machines.html', 
            pkg_dict=package, 
            custom_stage=stages, 
            machines_list=machines,
            machine_imageUrl=machine_imageUrl
            )
    
    def save_machines():
        package_name = request.form.get('package')
        resources_len = 0
        if package_name == None:
            return toolkit.abort(403, "bad request")
        
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})
            resources_len = len(package['resources'])

        except:
            return toolkit.abort(400, "Package not found") 
        
        if not Helper.check_access_edit_package(package['id']): 
            return toolkit.abort(403, "You are not authorized to access this function" )
               
        action = request.form.get('save_btn')
        if action == 'go-dataset-veiw': # I will add it later button
            return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
        
        if action == 'finish_machine':
            result = Helper.add_machine_links(request, resources_len)
            if result != false:
                return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))    

            return toolkit.abort(500, "Server issue")    

        return toolkit.abort(403, "bad request")
    

    def edit_machines_view(id):
        if not Helper.check_access_edit_package(id): 
            return toolkit.abort(403, "You are not authorized to access this function" )

        package = toolkit.get_action('package_show')({}, {'name_or_id': id})        
        machines, machine_imageUrl = Helper.get_machines_list()
        resource_machine_data = {}
        for resource in package['resources']:
            record = Helper.get_machine_link(resource['id'])
            if record and record.url not in resource_machine_data.keys():
                resource_machine_data[record.url] = [resource['id']]
            elif record:
                resource_machine_data[record.url].append(resource['id'])

        return render_template('edit_machines.html', 
            pkg_dict=package, 
            machines_list=machines, 
            resource_data=resource_machine_data,
            machine_imageUrl=machine_imageUrl,
            machines_count=len(resource_machine_data.keys())
            )
    

    def edit_save():
        package_name = request.form.get('package')
        package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})
        if not Helper.check_access_edit_package(package['id']): 
            return toolkit.abort(403, "You are not authorized to access this function" )

        resources_len = int(request.form.get('resources_length'))
        action = request.form.get('save_btn')
        if action == 'go-dataset-veiw': # cancel button
            return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
        
        if action == 'update_machine':
            result = Helper.update_resource_machine(request, resources_len, package)
            if result:
                return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))    

            return toolkit.abort(500, "Server issue")    

        return toolkit.abort(403, "bad request")
    
    

    def get_machine_link(id):
        if not toolkit.g.user: 
            return toolkit.abort(403, "You are not authorized to access this function" )
        record = Helper.get_machine_link(id)
        if record == false or record.url == '0':
            return '0'
        return json.dumps([record.url, record.link_name])
    
    
    def cancel_dataset_plugin_is_enabled():
        if Helper.check_plugin_enabled('cancel_dataset_creation'):
            return True
        return False

