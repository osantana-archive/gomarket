#!/usr/bin/env python
# -*- coding=utf-8 -*-

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from gae.index import getByName

class CountryLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Country',
                         [('name', str),
                          ])

if __name__ == '__main__':
  bulkload.main(CountryLoader())
