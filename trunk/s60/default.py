# -*- coding: utf-8 -*-
# 
#  default.py
#  comprices
#  
#  Created by Osvaldo Santana on 2009-02-27.
#  Copyright 2009 Triveos Tecnologia Ltda. All rights reserved.
# 

import os

TEST = False
if TEST:
    import sys
    sys.path.append("E:\\Python")

import e32     # pylint: disable-msg=F0401
import appuifw # pylint: disable-msg=F0401

from skel import AppSkel
from dataman import ConnectionError, InvalidSetting, DataManager

APP_NAME = u"comprices"
APP_VERSION = u"0.1"

class EntityChooser(object):
    def __init__(self, index, dataman):
        self.index = index
        self.dataman = dataman

        self._lb_lock = e32.Ao_lock()
        self._lb_selected = False

    def get(self, add_callback):
        option_keys = [None]
        option_values = [u'NEW']
        try:
            for key, value in self.dataman.entities[self.index].object_list():
                option_keys.append(key)
                option_values.append(value)
        except (ConnectionError, InvalidSetting), e:
            appuifw.note(unicode(e), 'error')
            return
            
        selection = appuifw.selection_list(option_values, 1)
        if selection is None:
            return

        key = option_keys[selection]
        value = option_values[selection]

        # add new item
        if key is None:
            key = add_callback(self.dataman)

        return key

    def get_with_lb(self, add_callback):
        option_keys = [None]
        option_values = [ (u'NEW', u'') ]
        try:
            for key, value in self.dataman.entities[self.index].object_list():
                option_keys.append(key)
                if u'\n' in value:
                    option_value = tuple(value.split(u'\n'))
                else:
                    option_value = (value, u'')
                option_values.append(option_value)
        except InvalidSetting, e:
            appuifw.note(unicode(e), 'error')
            return
        except ConnectionError:
            return
            
        old_body = appuifw.app.body
        old_exit = appuifw.app.exit_key_handler
        old_menu = appuifw.app.menu

        listbox = appuifw.Listbox(option_values, self._lb_callback)
        appuifw.app.body = listbox
        appuifw.app.exit_key_handler = self._lb_cancel_callback
        appuifw.app.menu = [ (u'Select', self._lb_callback) ]
        self._lb_lock.wait()

        appuifw.app.body = old_body
        appuifw.app.exit_key_handler = old_exit
        appuifw.app.menu = old_menu

        selection = listbox.current()
        if not self._lb_selected:
            return

        key = option_keys[selection]
        value = option_values[selection]

        # add new item
        if key is None:
            key = add_callback(self.dataman)

        return key

    def _lb_callback(self):
        self._lb_selected = True
        self._lb_lock.signal()

    def _lb_cancel_callback(self):
        self._lb_selected = False
        self._lb_lock.signal()


class MainApp(AppSkel):
    """This is the Application class"""

    TAB_SETTINGS = 0
    TAB_RESULTS = 1

    def __init__(self):
        self.title = u"ComPrices"
        self.dataman = DataManager(self.get_datadir(APP_NAME))

        self.settings_list = []
        self.load_settings_list()
        self.settings_lb = appuifw.Listbox(self.settings_list, self.tab_callback_settings)
        
        self.results_list = self.create_results_list()
        self.results_lb = appuifw.Listbox(self.results_list[0], self.tab_callback_results)

        super(MainApp, self).__init__(TEST)

    def setup(self):
        if self.dataman.stores.get():
            self.activate_tab(self.TAB_RESULTS)
        else:
            self.activate_tab(self.TAB_SETTINGS)

    def tabs(self):
        return (
            (u'Settings', self.tab_settings_body, self.tab_settings_menu),
            (u'Result', self.tab_results_body, self.tab_results_menu),
        )

    def tab_settings_body(self):
        return self.settings_lb

    def tab_settings_menu(self):
        return [
            (u'Change', self.tab_callback_settings),
            (u'Refresh', self.refresh),
        ]

    def load_settings_list(self):
        self.settings_list = [
            (u'Country', self.dataman.countries.get_name()),
            (u'State', self.dataman.states.get_name()),
            (u'City', self.dataman.cities.get_name()),
            (u'Store', self.dataman.stores.get_name().split(u'\n')[0]),
        ]

    def refresh_settings_lb(self, current=0):
        if self.settings_lb:
            self.settings_lb.set_list(self.settings_list, current)

    def tab_callback_settings(self):
        index = self.settings_lb.current()

        chooser = EntityChooser(index, self.dataman)
        if index == self.dataman.MANAGER_COUNTRY:
            country_key = chooser.get(self._add_country)
            if country_key:
                self.dataman.countries.set(country_key)
        elif index == self.dataman.MANAGER_STATE:
            state_key = chooser.get(self._add_state)
            if state_key:
                self.dataman.states.set(state_key)
        elif index == self.dataman.MANAGER_CITY:
            city_key = chooser.get(self._add_city)
            if city_key:
                self.dataman.cities.set(city_key)
        else:
            store_key = chooser.get_with_lb(self._add_store)
            if store_key:
                self.dataman.stores.set(store_key)

        self.load_settings_list()
        self.refresh_settings_lb(index)
        
        self.results_list = self.create_results_list()
        self.refresh_results_lb(self.results_list[0])
        
        if self.dataman.stores.get():
            self.activate_tab(self.TAB_RESULTS)

    def _add_country(self, dataman):
        country_name = appuifw.query(u"Country Name:", 'text')
        if country_name is None:
            return
        try:
            return dataman.countries.add(country_name)
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')

    def _add_state(self, dataman):
        state_name = appuifw.query(u"State Name:", 'text')
        if state_name is None:
            return
        try:
            return dataman.states.add(state_name)
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')

    def _add_city(self, dataman):
        city_name = appuifw.query(u"City Name:", 'text')
        if city_name is None:
            return
        try:
            return dataman.cities.add(city_name)
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')

    def _add_store(self, dataman):
        try:
            store_name, store_address = appuifw.multi_query(u"Store Name:", u"Address:")
        except ValueError:
            return
        try:
            return dataman.stores.add(store_name + u'\n' + store_address)
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')

    def tab_results_body(self):
        return self.results_lb

    def tab_results_menu(self):
        return [
            (u'Get Prices', self.get_prices),
        ]

    def tab_callback_results(self):
        index = self.results_lb.current()
        if index:
            appuifw.note(u"%s - %s" % (self.results_list[0][index][0], self.results_list[1][index]))
        else:
            self.get_prices()

    def refresh_results_lb(self, results):
        self.results_lb.set_list(results)

    def get_prices(self):
        if not self.dataman.stores.get():
            appuifw.note(u"Please, choose the store where you are.", "error")
            self.activate_tab(self.TAB_SETTINGS)
            return

        barcode = appuifw.query(u"Barcode:", 'text')
        if barcode is None:
            return
            
        if not self.dataman.verify_barcode(barcode):
            appuifw.note(u"Invalid barcode.", "error")
            return

        price = appuifw.query(u"Price:", 'float', 1.99)
        if not price:
            return

        description = appuifw.query(u"Description (optional):", 'text')
        if description is None:
            description = u""

        try:
            prices = self.dataman.get_prices(barcode, price, description)
            if not prices:
                appuifw.note(u'No prices for code %s' % (barcode,), 'info')

            self.results_list = self.create_results_list(prices, barcode)
            self.refresh_results_lb(self.results_list[0])
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')

    def create_results_list(self, prices=None, barcode=u""):
        if prices is None:
            prices = []

        current_store_name = self.dataman.stores.get_name().split(u'\n')[0]

        if barcode:
            prices_list = [ (u'Get Prices', u"%s / %s" % (current_store_name, barcode)) ]
        else:
            prices_list = [ (u'Get Prices', current_store_name) ]
        store_addresses = [ None ]

        for price in prices:
            store_name, store_address = price[0].split(u'\n')
            prices_list.append( (store_name, price[1]) )
            store_addresses.append(store_address)
        return prices_list, store_addresses


    def refresh(self):
        try:
            self.dataman.refresh()
        except ConnectionError, e:
            appuifw.note(unicode(e), 'error')
            return
            
        self.load_settings_list()
        
        if self.settings_lb:
            self.load_settings_list()
            self.refresh_settings_lb()
        if self.results_lb:
            self.results_list = self.create_results_list()
            self.refresh_results_lb(self.results_list[0])

    def confirm_exit(self):
        self.dataman.close()
        return True

    def menu_about(self):
        if TEST:
            icon = "E:\\Python\\icon.png"
        else:
            icon = os.path.join(self.get_datadir(APP_NAME), "icon.png")
        self.about_dialog(
            name=u"ComPrices",
            version=u"0.1",
            year=u'2009',
            authors=[ u"Osvaldo Santana Neto", u"Ramiro Luz" ],
            icon=icon,
            license_=u"MIT License",
        )



def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
    main()
