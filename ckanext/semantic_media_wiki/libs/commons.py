# encoding: utf-8

import ckan.plugins.toolkit as toolkit


class Common():

    @staticmethod
    def get_action_context():
        return {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}


    @staticmethod
    def abort_if_dataset_editing_not_permit(package_id):
        context = Common.get_action_context()
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_update', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            toolkit.abort(403, 'You are not authorized to access this function')
    


    @staticmethod     
    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins", "")
        if plugin_name in plugins:
            return True
        return False


    @staticmethod
    def set_package_extra(package, key, value):
        extras = package.get('extras') or []
        updated = False
        for extra in extras:
            if extra.get('key') == key:
                extra['value'] = value
                updated = True
                break
        if not updated:
            extras.append({'key': key, 'value': value})
        package['extras'] = extras
        toolkit.get_action('package_update')(Common.get_action_context(), package)
