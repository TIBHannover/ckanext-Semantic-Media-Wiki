# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.semantic_media_wiki.controllers.media_wiki import MediaWikiController



class SampleLinkPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'ckanext-semantic-media-wiki')


    #plugin Blueprint

    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        

        return blueprint
    
    # def get_helpers(self):
    #     return {'cancel_dataset_is_enabled': MediaWikiController.cancel_dataset_plugin_is_enabled,
    #     'get_smw_link': MediaWikiController.get_smw_link}
