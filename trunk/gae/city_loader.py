#!/usr/bin/env python
# -*- coding=utf-8 -*-

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from index import getByName, State


def getStateByName(name):
    state = getByName(name=name,
                      modelClass=State)
    return state.key()

class StateLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'City',
                         [('name', str),
                          ('state', getStateByName),
                          ])

if __name__ == '__main__':
  bulkload.main(StateLoader())
