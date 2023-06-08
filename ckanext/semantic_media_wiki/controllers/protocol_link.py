# encoding: utf-8

from flask import request, redirect, render_template
from datetime import datetime as _time
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
import json
from ckanext.semantic_media_wiki.models.dataset_protocol_link import DatasetProtocolLink
from ckanext.semantic_media_wiki.libs.commons import Common



class ProtocolLinkController():

    @staticmethod
    def index():
        return "0"


    @staticmethod
    def save_protocol_link():
        try:            
            dataset_id = request.form.get('dataset_id')
            Common.abort_if_dataset_editing_not_permit(dataset_id)
            protocol_url = request.form.get('protocol_url')
            protocol_name = request.form.get('protocol_name')
            created_at = _time.now()
            updated_at = created_at            
            db_model = DatasetProtocolLink(
                    dataset_id=dataset_id, 
                    protocol_url=protocol_url, 
                    protocol_name=protocol_name, 
                    created_at=created_at, 
                    updated_at=updated_at
            )
            db_model.save()
            return redirect(h.url_for('dataset.read', id=str(dataset_id) ,  _external=True))

        except:
            # raise
            return toolkit.abort(500, "Server issue")
    



    @staticmethod
    def get_protocol_link(dataset_id):
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': dataset_id})
            db_object = DatasetProtocolLink(dataset_id=dataset_id)
            protocol_link_obj = db_object.get_by_dataset(id=dataset_id)
            protocols = {}
            for res in protocol_link_obj:
                protocols[res.protocol_name] = res.protocol_url
            return json.dumps(protocols)
        except:
            # raise
            return json.dumps({})



    @staticmethod
    def protocol_edit_view(dataset_id):
        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': dataset_id})
            db_object = DatasetProtocolLink(dataset_id=dataset_id)
            protocol_link_obj = db_object.get_by_dataset(id=dataset_id)
            protocols = {}
            for res in protocol_link_obj:
                protocols[res.protocol_name] = res.protocol_url
            return render_template('edit_protocols.html', protocols=protocols, pkg_dict=package)
        except:
            # raise
            return toolkit.abort(404, "Not Found")


