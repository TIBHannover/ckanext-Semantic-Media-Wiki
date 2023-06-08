# encoding: utf-8

from flask import request, redirect
from datetime import datetime as _time
import ckan.lib.helpers as h
from ckanext.semantic_media_wiki.models.dataset_protocol_link import DatasetProtocolLink



class ProtocolLinkController():

    @staticmethod
    def index():
        return "0"


    @staticmethod
    def save_protocol_link():
        try:
            dataset_id = request.form.get('dataset_id')
            protocol_url = request.form.get('protocol_url')
            protocol_name = request.form.get('protocol_name')
            created_at = _time.now()
            updated_at = create_at
            db_model = DatasetProtocolLink(
                    dataset_id==dataset_id, 
                    protocol_url==protocol_url, 
                    protocol_name=protocol_name, 
                    created_at=created_at, 
                    updated_at=updated_at
            )
            db_model.save()
            return redirect(h.url_for('dataset.read', id=str(dataset_id) ,  _external=True))

        except:
            return toolkit.abort(500, "Server issue")
    



    @staticmethod
    def get_protocol_link(dataset_id):
        try:
            db_object = DatasetProtocolLink(dataset_id==dataset_id)
            protocol_link_obj = db_object.get_by_dataset(id=dataset_id)
            return protocol_link_obj
        except:
            return {}


