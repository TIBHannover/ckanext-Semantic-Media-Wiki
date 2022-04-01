# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper


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
        return '0'
    


    def cancel_dataset_plugin_is_enabled():
        if SampleLinkHelper.check_plugin_enabled('cancel_dataset_creation'):
            return True
        return False