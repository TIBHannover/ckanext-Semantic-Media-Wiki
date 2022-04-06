# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.semantic_media_wiki.controllers.sample_link import SampleLinkController



class SampleLinkPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/sample_link')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics/sample_link', 'ckanext-sample-link')


    #plugin Blueprint

    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'

        blueprint.add_url_rule(
            u'/smw/add_samples_view/<id>',
            u'add_samples_view',
            SampleLinkController.add_samples_view,
            methods=['GET']
            )
        
        blueprint.add_url_rule(
            u'/smw/save_samples',
            u'save_samples',
            SampleLinkController.save_samples,
            methods=['POST']
            )
        
        blueprint.add_url_rule(
            u'/smw/get_samples_link/<id>',
            u'get_samples_link',
            SampleLinkController.get_samples_link,
            methods=['GET']
            )
        

        return blueprint
    
    def get_helpers(self):
        return {'cancel_dataset_is_enabled': SampleLinkController.cancel_dataset_plugin_is_enabled}
