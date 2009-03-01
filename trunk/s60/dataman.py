# -*- coding: utf-8 -*-
#
#  dataman.py
#  comprices
#
#  Created by Osvaldo Santana on 2009-02-27.
#  Copyright 2009 Triveos Tecnologia Ltda. All rights reserved.
#

import os
import urllib

import e32dbm  # pylint: disable-msg=F0401

import simplejson as json

from skel import Connection
from utils import verify_barcode

DB_MODE = 'cf'
SERVER_URL = "http://comprices.appspot.com"
    
class ConnectionError(Exception):
    pass

def _urlopen(path, args, method="get"):
    connection = Connection.get_instance()
    connection.start()
    if not connection.started():
        raise ConnectionError(u"Error establishing connection.")

    query = urllib.urlencode(args)
    if method == "get":
        url = "%s/%s/?%s" % (SERVER_URL, path, query)
    else:
        url = "%s/%s/" % (SERVER_URL, path)

    try:
        if method == "get":
            request = urllib.urlopen(url)
        else:
            request = urllib.urlopen(url, query)

        json_response = request.read()

        try:
            return json.loads(json_response)
        except ValueError:
            raise ConnectionError(u"Invalid server response")
        request.close()
    except IOError:
        raise ConnectionError(u"Error reading server response")

class InvalidSetting(Exception):
    pass

class Entities(object):
    _order = 0
    def get_order(cls):
        cls._order += 1
        return cls._order - 1
    get_order = classmethod(get_order)

    def __init__(self, key, url_path, manager, database):
        self.order = Entities.get_order()
        self.key = key
        self.url_path = url_path
        self.manager = manager
        self.cache = e32dbm.open(database, DB_MODE)

    def set(self, value):
        self.manager.set_config(self.key, value)
        self.manager.clear(self.order + 1)

    def get(self):
        return self.manager.get_config(self.key, u'')

    def get_name(self):
        if not self.cache.has_key(self.get()):
            return u''
        name = self.cache[self.get()]
        if isinstance(name, str):
            try:
                return name.decode('utf-8')
            except UnicodeError:
                return name.decode('latin1')
        return name

    def request_key(self):
        if not self.order:
            return u''
        previous_key = self.manager.get_entity_by_order(self.order - 1).key
        if not self.manager.get_config(previous_key, u''):
            raise InvalidSetting(u"Please, choose a %s." % (previous_key,))
        return self.manager.get_config(previous_key, u'')


    def request(self, request_key):
        return _urlopen(self.url_path, {'key': request_key })

    def object_list(self):
        if not len(self.cache):
            try:
                self.refresh()
            except KeyError: # Parent is a NEW object
                return []

        object_list = []
        for k, v in self.cache.items():
            if isinstance(k, unicode):
                unicode_key = k
            else:
                try:
                    unicode_key = k.decode('utf-8')
                except UnicodeError:
                    unicode_key = k.decode('latin1')
            if isinstance(v, unicode):
                unicode_value = v
            else:
                try:
                    unicode_value = v.decode('utf-8')
                except UnicodeError:
                    unicode_value = v.decode('latin1')
            object_list.append( (unicode_key, unicode_value) )
        object_list.sort(lambda x, y: cmp(x[1], y[1]))
        return object_list

    def clear(self):
        self.cache.clear()
        self.cache.sync()

    def refresh(self):
        request_key = self.request_key()
        self.cache.clear()
        self.cache.update(self.request(request_key))
        self.cache.sync()

    def close(self):
        Connection.get_instance().stop()
        self.cache.close()

    def add(self, value):
        key = _urlopen(path=self.url_path, args={'name': value, 'key': self.request_key()}, method="post")
        self.cache[key] = value
        return key


class DataManager(object):
    MANAGER_COUNTRY = 0
    MANAGER_STATE = 1
    MANAGER_CITY = 2
    MANAGER_STORE = 3

    def __init__(self, resourcedir):
        self.resourcedir = resourcedir

        filename = unicode(os.path.join(resourcedir, 'config'))
        self.config = e32dbm.open(filename, DB_MODE)

        self.entities = [
            Entities(u'country', u'countries', self, os.path.join(resourcedir, 'countries')),
            Entities(u'state', u'states', self, os.path.join(resourcedir, 'states')),
            Entities(u'city', u'cities', self, os.path.join(resourcedir, 'cities')),
            Entities(u'store', u'stores', self, os.path.join(resourcedir, 'stores')),
        ]

        self.countries = self.entities[self.MANAGER_COUNTRY]
        self.states = self.entities[self.MANAGER_STATE]
        self.cities = self.entities[self.MANAGER_CITY]
        self.stores = self.entities[self.MANAGER_STORE]

    def get_entity_by_order(self, order):
        return self.entities[order]

    def set_config(self, key, value):
        self.config[key] = value

    def get_config(self, key, default):
        if not self.config.has_key(key):
            self.config[key] = default
        return self.config[key]

    def clear(self, clear_from):
        try:
            self.entities[clear_from].set(u'')
            self.entities[clear_from].clear()
        except IndexError:
            return

    def refresh(self):
        for entity in self.entities:
            try:
                entity.refresh()
            except InvalidSetting:
                break
            except ConnectionError:
                break

    def close(self):
        for entity in self.entities:
            entity.close()
        self.config.close()

    def verify_barcode(self, barcode):
        return verify_barcode(barcode)

    def get_prices(self, barcode, price, description):
        query = {
            'barcode': barcode,
            'price': price,
        }
        if description:
            query['description'] = description
        
        if self.get_config('store', u''):
            query['key'] = self.get_config('store', u'')    
        return _urlopen("prices", query)
