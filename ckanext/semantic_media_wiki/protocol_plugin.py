# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.semantic_media_wiki.controllers.protocol_link import ProtocolLinkController



class ProtocolLinkPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/protocol_link')
        toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('public/statics/sample_link', 'ckanext-sample-link')
    


    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'

        blueprint.add_url_rule(
            u'/smw/protocol_index',
            u'protocol_index',
            ProtocolLinkController.index,
            methods=['GET']
            )                
        

        return blueprint