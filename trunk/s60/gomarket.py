#!/usr/bin/env python
# encoding: utf-8

import os
import sys
sys.path.append("E:\\Python")

from skel import *

APP_NAME = u"gomarket"
APP_VERSION = u"0.1"

class DataManager(object):
    _instance = None

    def __init__(self):
        self._locations = {
            u'Brazil': {
                u'São Paulo': [
                    u'São Paulo',
                    u'São José do Rio Preto',
                ],
                u'Rio de Janeiro': [
                    u'Rio de Janeiro',
                    u'Niterói',
                ],
            },
            u'USA': {
                u'Massachusetts': [
                    u'Boston',
                    u'Springfield',
                ],
            },
        }

        self.config = {
            'country': u'Brazil',
            'state': u'São Paulo',
            'city': u'São Paulo',
        }


    def countries(self):
        country_list = self._locations.keys()
        country_list.sort()
        return country_list

    def states(self):
        state_list = self._locations[self.config['country']].keys()
        state_list.sort()
        return state_list

    def cities(self):
        city_list = self._locations[self.config['country']][self.config['state']]
        city_list.sort()
        return city_list

    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    get_instance = classmethod(get_instance)

    def save(self):
        pass

    def refresh(self):
        pass



class MainApp(AppSkel):
    """This is the Application class"""

    def setup(self):
        self.title = u"GoMarket"

    def tab_settings(self):
        datamanager = DataManager.get_instance()

        self.settings_list = [
            (u'Country', datamanager.config['country']),
            (u'State', datamanager.config['state']),
            (u'City', datamanager.config['city']),
        ]
        self.settings_lb = appuifw.Listbox(self.settings_list, self.tab_callback_settings)
        return self.settings_lb

    def tab_callback_settings(self):
        index = self.settings_lb.current()
        datamanager = DataManager.get_instance()
        row = self.settings_list[index]

        try:
            if row[0] == "Country":
                options = datamanager.countries()
            elif row[0] == "State":
                options = datamanager.states()
            elif row[0] == "City":
                options = datamanager.cities()
            else:
                raise ValueError("Invalid option '%s'." % (selected[0],))
        except KeyError:
            options = []
        options.insert(0, u'NEW ')

        selection = appuifw.selection_list(options, 1)
        if selection is None:
            return
        option = options[selection]

        if option == u'NEW ':
            option = appuifw.query(u"New %s" % row[0], 'text')

        self.settings_list[index] = (row[0], option)
        for i in range(index + 1, len(self.settings_list)):
            self.settings_list[i] = (self.settings_list[i][0], u'')
        self.settings_lb.set_list(self.settings_list, index)

        datamanager.config['country'] = self.settings_list[0][1]
        datamanager.config['state'] = self.settings_list[1][1]
        datamanager.config['city'] = self.settings_list[2][1]
        # TODO datamanager.save()

    def tab_result(self):
        results = appuifw.Listbox([u'result'], self.tab_callback_result)
        return results

    def tab_callback_result(self):
        pass

    def tab_stores(self):
        results = appuifw.Listbox([u'stores'], self.tab_callback_stores)
        return results

    def tab_callback_stores(self):
        pass


    def tabs(self):
        tabs = (
            (u'Settings', self.tab_settings),
            (u'Stores', self.tab_stores),
            (u'Result', self.tab_result),
        )
        return tabs

    def menu(self):
        return [
            (u'Get Price', self.get_price),
            (u'Refresh', self.refresh),
        ]

    def get_price(self):
        pass

    def refresh(self):
        datamanager = DataManager.get_instance()
        datamanager.refresh()
        datamanager.save()

    def menu_help(self):
        pass

    def menu_about(self):
        pass

def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
	main()
