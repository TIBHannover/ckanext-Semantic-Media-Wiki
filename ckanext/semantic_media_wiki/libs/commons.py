# encoding: utf-8

import ckan.plugins.toolkit as toolkit


class Common():

    @staticmethod
    def abort_if_dataset_editing_not_permit(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_update', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            toolkit.abort(403, 'You are not authorized to access this function')
    


    @staticmethod     
    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False