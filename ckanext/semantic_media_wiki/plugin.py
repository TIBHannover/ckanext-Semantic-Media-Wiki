import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.semantic_media_wiki.controllers.media_wiki import MediaWikiController



class SemanticMediaWikiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/machine_link')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics/machine_link', 'ckanext-semantic-media-wiki')


    #plugin Blueprint

    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        blueprint.add_url_rule(
            u'/smw/machines_view/<id>',
            u'machines_view',
            MediaWikiController.machines_view,
            methods=['GET']
            )
        blueprint.add_url_rule(
            u'/smw/save_machines',
            u'save_machines',
            MediaWikiController.save_machines,
            methods=['POST']
            )
        
        blueprint.add_url_rule(
            u'/smw/edit_machines_view/<id>',
            u'edit_machines_view',
            MediaWikiController.edit_machines_view,
            methods=['GET']
            )
        
        blueprint.add_url_rule(
            u'/smw/get_machine_link/<id>',
            u'get_machine_link',
            MediaWikiController.get_machine_link,
            methods=['GET']
            )
        
        blueprint.add_url_rule(
            u'/smw/get_resource_machine/<id>',
            u'get_resource_machine',
            MediaWikiController.get_resource_machine,
            methods=['GET']
            )
        
        blueprint.add_url_rule(
            u'/smw/edit_save',
            u'edit_save',
            MediaWikiController.edit_save,
            methods=['POST']
            )

        return blueprint
    
    def get_helpers(self):
        return {'cancel_dataset_is_enabled': MediaWikiController.cancel_dataset_plugin_is_enabled,
        'get_smw_link': MediaWikiController.get_smw_link}
