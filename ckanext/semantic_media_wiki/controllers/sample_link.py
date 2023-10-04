# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template, request, redirect
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
import ckan.lib.helpers as h
import json
from ckanext.semantic_media_wiki.libs.commons import Common



class SampleLinkController():

    def add_samples_view(id):
        Common.abort_if_dataset_editing_not_permit(id)        
        package = toolkit.get_action('package_show')({}, {'name_or_id': id})
        stages = True
        samples = SampleLinkHelper.get_samples_list()
        return render_template('add_samples.html', 
            pkg_dict=package, 
            samples=samples,
            custom_stage=stages
            )
    


    def save_samples():
        package_name = request.form.get('package')
        sample_count = request.form.get('sample_count')
        if package_name == None:
            return toolkit.abort(403, "bad request")
        
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})

        except:
            return toolkit.abort(400, "Package not found") 
        
        Common.abort_if_dataset_editing_not_permit(package['id'])                       
        action = request.form.get('save_btn')
        if action == 'go-dataset-veiw': # I will add it later button
            return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
        
        if action == 'finish_machine':
            result = SampleLinkHelper.add_sample_links(request, int(sample_count))
            if result != False:
                return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))    

            return toolkit.abort(500, "Server issue")    

        return toolkit.abort(403, "bad request")
    



    def get_samples_link(id):
        if not toolkit.g.user: 
            return toolkit.abort(403, "You are not authorized to access this function" )
                
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': id})
            sample_links = []
            results = []
            for res in package['resources']:
                sample_urls = SampleLinkHelper.get_sample_link(res['id'])
                if len(sample_urls.keys()) == 0:
                    continue
                for name, link in sample_urls.items():
                    if link not in sample_links:
                        sample_links.append(link)
                        eq_name = name
                        if name == '':
                            eq_name = "Link to the Sample"
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



    def get_resource_sample(id):
        urls = SampleLinkHelper.get_sample_link(id)
        if len(urls.keys()) == 0:
            return '0'
        return json.dumps(urls)



    def edit_samples_view(id):        
        Common.abort_if_dataset_editing_not_permit(id)
        package = toolkit.get_action('package_show')({}, {'name_or_id': id})
        samples = SampleLinkHelper.get_samples_list()
        resource_sample_data = {}
        sample_link_name = {}
        for resource in package['resources']:
            urls = SampleLinkHelper.get_sample_link(resource['id'])
            for name, url in urls.items(): 
                try:
                    resource_sample_data[url].append(resource['id'])
                except KeyError:
                    resource_sample_data[url] = [resource['id']]
                    sample_link_name[url] = name                                    

        return render_template('edit_samples.html', 
            pkg_dict=package, 
            samples_list=samples, 
            resource_data=resource_sample_data,
            samples_count=len(resource_sample_data.keys()),
            sample_link_name=sample_link_name
            )
    


    def edit_save_samples():
        package_name = request.form.get('package')
        sample_count = request.form.get('sample_count')  
        package = toolkit.get_action('package_show')({}, {'name_or_id': package_name})
        Common.abort_if_dataset_editing_not_permit(package['id'])        
        action = request.form.get('save_btn')
        if action == 'go-dataset-veiw': # cancel button
            return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True)) 
        
        if action == 'update_sample':
            result = SampleLinkHelper.update_resource_sample(request, int(sample_count), package)
            if result:
                return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))    

            return toolkit.abort(500, "Server issue")    

        return toolkit.abort(403, "bad request")



    def get_samples_for_a_resource(resourec_id):
        urls = SampleLinkHelper.get_sample_link(resourec_id)
        if len(urls.keys()) == 0:
            return {}
        return urls
    
