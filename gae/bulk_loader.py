#!/usr/bin/env python
# -*- coding=utf-8 -*-

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from index import getByName, State, City

import index

class StateLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'State',
                         [('name', str),
                          ('state', str),
                          ])

  def HandleEntity(self, entity):
    entity.state = get_state_by_name(entity.state) 
    return entity

def get_state_by_name(name):
    return getByName(name=name,
                     modelClass=State)

class CityLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'City',
                         [('name', str),
                          ('state', City.get_by_name),
                          ])

def get_city_by_name(name):
    return getByName(name=name,
                     modelClass=City)


class CountryLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Country',
                         [('name', str),
                          ])

if __name__ == '__main__':
  bulkload.main(CountryLoader(),
                StateLoader(),
                CityLoader()
               )
