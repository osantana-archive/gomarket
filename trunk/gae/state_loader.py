#!/usr/bin/env python
# -*- coding=utf-8 -*-

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types

import index

def get_state_by_name(name):
    return index.getByName(name=name,
                           modelClass=index.State)

class StateLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'index.State',
                         [('name', unicode),
                          ('country', get_state_by_name)
                          ])

if __name__ == '__main__':
  bulkload.main(StateLoader())
