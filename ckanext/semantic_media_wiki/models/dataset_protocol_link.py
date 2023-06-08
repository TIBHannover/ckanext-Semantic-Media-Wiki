# encoding: utf-8

import datetime
from sqlalchemy import Column, Table, ForeignKey, orm
from sqlalchemy import types as _types
from sqlalchemy.sql.expression import false
from ckan.model import meta, Package, domain_object


__all__ = [u"DatasetProtocolLink", u"dataset_protocol_link_table"]

dataset_protocol_link_table = Table(
    u"dataset_protocol_link",
    meta.metadata,
    Column(u"id", _types.Integer, primary_key=True, nullable=False),
    Column(u"dataset_id", _types.UnicodeText, ForeignKey(u"package.id"), nullable=False),
    Column(u"protocol_url", _types.UnicodeText, nullable=False),
    Column(u"protocol_name", _types.UnicodeText),
    Column(u"created_at", _types.DateTime, default=datetime.datetime.utcnow, nullable=False),
    Column(u"updated_at", _types.DateTime, default=datetime.datetime.utcnow, nullable=False),
)

class DatasetProtocolLink(domain_object.DomainObject):
    def __init__(self, dataset_id=None, protocol_url=None, protocol_name=None, created_at=None, updated_at=None):
        self.dataset_id = dataset_id
        self.protocol_url = protocol_url
        self.protocol_name = protocol_name
        self.created_at = created_at
        self.updated_at = updated_at
    

    @classmethod
    def get_by_dataset(cls, id, autoflush=True):
        if not id:
            return None

        exists = meta.Session.query(cls).filter(cls.dataset_id==id).first() is not None
        if not exists:
            return False
        query = meta.Session.query(cls).filter(cls.dataset_id==id)
        query = query.autoflush(autoflush)
        record = query
        return record

    
    def get_resource(self):
        return self.resource



meta.mapper(
    DatasetProtocolLink,
    dataset_protocol_link_table,
    properties={
        u"package": orm.relation(
            Package, backref=orm.backref(u"dataset_protocol_link", cascade=u"all, delete, delete-orphan")
        )
    },
)







