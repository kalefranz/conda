# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from functools import total_ordering

from .enums import LinkType, NoarchType, Platform
from .._vendor.auxlib.decorators import memoizedproperty
from .._vendor.auxlib.entity import (BooleanField, ComposableField, DictSafeMixin, Entity,
                                     EnumField, Field, IntegerField, ListField, MapField,
                                     StringField)
from ..common.compat import string_types


@total_ordering
class Priority(object):

    def __init__(self, priority):
        self._priority = priority

    def __int__(self):
        return self._priority

    def __lt__(self, other):
        return self._priority < int(other)

    def __eq__(self, other):
        return self._priority == int(other)

    def __repr__(self):
        return "Priority(%d)" % self._priority


class PriorityField(Field):
    _type = (int, Priority)

    def unbox(self, instance, instance_type, val):
        return int(val)


class LinkTypeField(EnumField):
    def box(self, instance, val):
        if isinstance(val, string_types):
            val = val.replace('-', '').replace('_', '').lower()
            if val == 'hard':
                val = LinkType.hardlink
            elif val == 'soft':
                val = LinkType.softlink
        return super(LinkTypeField, self).box(instance, val)


class NoarchField(EnumField):
    def box(self, instance, val):
        return super(NoarchField, self).box(instance, NoarchType.coerce(val))


class Link(DictSafeMixin, Entity):
    source = StringField()
    type = LinkTypeField(LinkType, required=False)


EMPTY_LINK = Link(source='')


class IndexJsonRecord(DictSafeMixin, Entity):
    _lazy_validate = True

    arch = StringField(required=False, nullable=True)
    build = StringField()
    build_number = IntegerField()
    date = StringField(required=False)
    depends = ListField(string_types, required=False)
    features = StringField(required=False)
    has_prefix = BooleanField(required=False)
    license = StringField(required=False)
    license_family = StringField(required=False)
    md5 = StringField(required=False, nullable=True)
    name = StringField()
    noarch = NoarchField(NoarchType, required=False, nullable=True)
    platform = EnumField(Platform, required=False, nullable=True)
    preferred_env = StringField(default=None, required=False, nullable=True)
    size = IntegerField(required=False)
    track_features = StringField(required=False)
    version = StringField()

    @property
    def dist_name(self):
        return "%s-%s-%s" % (self.name, self.version, self.build)


class IndexRecord(IndexJsonRecord):

    fn = StringField()
    schannel = StringField(required=False, nullable=True)
    channel = StringField(required=False, nullable=True)
    priority = PriorityField(required=False)
    url = StringField()
    auth = StringField(required=False, nullable=True)
    subdir = StringField(required=False)

    @memoizedproperty
    def pkey(self):
        if self.name.endswith('@'):
            return self.name
        return "%s::%s" % (self.schannel, self.dist_name) if self.schannel else self.dist_name

    def __hash__(self):
        return hash(self.pkey)

    def __eq__(self, other):
        return hash(self) == hash(other)


class LinkedPackageRecord(IndexRecord):
    files = ListField(string_types, default=(), required=False)
    link = ComposableField(Link, required=False)

    # url is optional here for legacy support.
    #   see tests/test_create.py test_dash_c_usage_replacing_python
    url = StringField(required=False, nullable=True)
