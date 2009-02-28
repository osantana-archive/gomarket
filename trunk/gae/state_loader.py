#!/usr/bin/env python
# -*- coding=utf-8 -*-

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from index import getByName, Country


def getCountryByName(name):
    country = getByName(name=name,
                        modelClass=Country)
    return country.key()

class StateLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'State',
                         [('name', str),
                          ('country', getCountryByName),
                          ])

if __name__ == '__main__':
  bulkload.main(StateLoader())
