# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template
from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
import json


class SampleLinkController():

    def add_samples_view(id):
        if not SampleLinkHelper.check_access_edit_package(id):
            toolkit.abort(403, 'You are not authorized to access this function')

        package = toolkit.get_action('package_show')({}, {'name_or_id': id})
        stages = True
        samples = SampleLinkHelper.get_samples_list()
        return json.dumps(samples)
        # return render_template('add_machines.html', 
        #     pkg_dict=package, 
        #     samples=samples,
        #     custom_stage=stages
        #     )