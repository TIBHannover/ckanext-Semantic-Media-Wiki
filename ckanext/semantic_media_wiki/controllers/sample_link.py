# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template, request, redirect
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
import ckan.lib.helpers as h
import json



class SampleLinkController():

    def add_samples_view(id):
        if not SampleLinkHelper.check_access_edit_package(id):
            toolkit.abort(403, 'You are not authorized to access this function')

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
        
        if not SampleLinkHelper.check_access_edit_package(package['id']): 
            return toolkit.abort(403, "You are not authorized to access this function" )
               
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




    def cancel_dataset_plugin_is_enabled():
        if SampleLinkHelper.check_plugin_enabled('cancel_dataset_creation'):
            return True
        return False