#!/usr/bin/env python
# encoding: utf-8
# SIS file infos:
# SYMBIAN_UID = 0xe89c6eaf
# SIS_VERSION = "0.1.0"


import os
import sys
import md5
sys.path.append("E:\\Python")

import e32     # pylint: disable-msg=F0401
import e32dbm  # pylint: disable-msg=F0401
import appuifw # pylint: disable-msg=F0401
import skel
import test_info

APP_NAME = u"gomarket"
APP_VERSION = u"0.1"
RESOURCE_DIR = "E:\\Python"
DB_MODE = 'cf' # TODO: change database open mode from 'nf' -> 'cf'


# http://www.pythonbrasil.com.br/moin.cgi/CodigoBarras
class InvalidBarcode(Exception):
    pass

def _compute_barcode_checksum(arg):
    weight = [1, 3] * 6
    magic = 10
    sum_ = 0

    for i in range(12):
        sum_ += int(arg[i]) * weight[i]
    digit = (magic - (sum_ % magic)) % magic
    if digit < 0 or digit >= magic:
        raise InvalidBarcode("Error validating barcode.")
    return digit

def _verify_barcode(bits):
    if len(bits) != 13:
        return False
    computed_checksum = _compute_barcode_checksum(bits[:12])
    codebar_checksum = bits[12]
    if codebar_checksum != computed_checksum:
        return False
    return True
#/


class InvalidSetting(Exception):
    pass

class Entities(object):
    _order = 0
    def get_order(cls):
        cls._order += 1
        return cls._order - 1
    get_order = classmethod(get_order)

    def __init__(self, key, manager, database):
        self.order = Entities.get_order()
        self.key = key
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
        return unicode(self.cache[self.get()])

    def request_key(self):
        if not self.order:
            return u''
        previous_key = self.manager.get_entity_by_order(self.order - 1).key
        if not self.manager.get_config(previous_key, u''):
            raise InvalidSetting(u"Please, choose a %s." % (previous_key,))
        return self.manager.get_config(previous_key, u'')

    def request(self, request_key):
        # TODO: implement with urllib...
        if self.key == u'country':
            return test_info.COUNTRIES_TEST
        elif self.key == u'state':
            return test_info.STATES_TEST[request_key]
        elif self.key == u'city':
            return test_info.CITIES_TEST[request_key]
        elif self.key == u'store':
            return test_info.STORES_TEST[request_key]
        else:
            raise ValueError("Invalid entity name %s." % (self.key,))

    def object_list(self):
        if not len(self.cache):
            self.refresh()
        object_list = [ (unicode(k), unicode(v)) for k, v in self.cache.items() ]
        object_list.sort(lambda x, y: cmp(x[1], y[1]))
        return object_list

    def clear(self):
        self.cache.clear()
        self.cache.sync()

    def refresh(self):
        self.cache.clear()
        self.cache.update(self.request(self.request_key()))
        self.cache.sync()

    def close(self):
        self.cache.close()

    def add(self, value):
        # TODO: urllib post and get new key...
        key = md5.md5(value).hexdigest()
        self.cache[unicode(key)] = unicode(value)
        return key


class DataManager(object):
    MANAGER_COUNTRY = 0
    MANAGER_STATE = 1
    MANAGER_CITY = 2
    MANAGER_STORE = 3

    def __init__(self, resourcedir):
        self.resourcedir = resourcedir

        self.config = e32dbm.open(os.path.join(resourcedir, 'config.db'), DB_MODE)

        self.entities = [
            Entities(u'country', self, os.path.join(resourcedir, 'countries.db')),
            Entities(u'state', self, os.path.join(resourcedir, 'states.db')),
            Entities(u'city', self, os.path.join(resourcedir, 'cities.db')),
            Entities(u'store', self, os.path.join(resourcedir, 'stores.db')),
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
            entity.refresh()

    def close(self):
        for entity in self.entities:
            entity.close()
        self.config.close()

    def verify_barcode(self, barcode):
        return _verify_barcode(str(barcode))

    def get_prices(self, barcode, price, description):
        # TODO: implement with urllib request...
        print "Get Price:", barcode, price, description
        if barcode == 978:
            return [
                (u'Supermercado Foo', u'R$10,00'),
                (u'Supermercado Bar', u'R$10,00'),
                (u'Supermercado Baz', u'R$10,00'),
            ]
        else:
            return []


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
        except InvalidSetting, e:
            appuifw.note(unicode(e), 'error')
            return
        except KeyError:
            pass

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
        except KeyError:
            pass

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


class MainApp(skel.AppSkel):
    """This is the Application class"""

    TAB_SETTINGS = 0
    TAB_RESULTS = 1

    def __init__(self):
        self.title = u"GoMarket"
        self.dataman = DataManager(RESOURCE_DIR)

        self.settings_list = []
        self.settings_lb = None

        self.results_lb = None

        super(MainApp, self).__init__()

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
        self.load_settings_list()
        self.settings_lb = appuifw.Listbox(self.settings_list, self.tab_callback_settings)
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
        self.refresh_results_lb(self.get_results_list([]))

    def _add_country(self, dataman):
        country_name = appuifw.query(u"Country Name:", 'text')
        if country_name is None:
            return
        return dataman.countries.add(country_name)

    def _add_state(self, dataman):
        state_name = appuifw.query(u"State Name:", 'text')
        if state_name is None:
            return
        return dataman.states.add(state_name)

    def _add_store(self, dataman):
        try:
            store_name, store_address = appuifw.multi_query(u"Store Name:", u"Address:")
        except ValueError:
            return
        return dataman.stores.add(store_name + u'\n' + store_address)

    def _add_city(self, dataman):
        city_name = appuifw.query(u"City Name:", 'text')
        if city_name is None:
            return
        return dataman.cities.add(city_name)

    def tab_results_body(self):
        results_list = self.get_results_list([])
        self.results_lb = appuifw.Listbox(results_list, self.tab_callback_results)
        return self.results_lb

    def tab_results_menu(self):
        return [
            (u'Get Prices', self.get_prices),
        ]

    def tab_callback_results(self):
        if self.results_lb.current() == 0:
            self.get_prices()

    def get_results_list(self, results, barcode=""):
        store_name = self.dataman.stores.get_name().split(u'\n')[0]
        if barcode:
            results_list = [ (u'Get Prices', u"%s / %s" % (store_name, barcode)) ]
        else:
            results_list = [ (u'Get Prices', store_name) ]
        results_list += results
        return results_list

    def refresh_results_lb(self, results):
        self.results_lb.set_list(results)

    def get_prices(self):
        if not self.dataman.stores.get():
            appuifw.note(u"Please, choose the store where you are.", "error")
            self.activate_tab(self.TAB_SETTINGS)
            return

        barcode = appuifw.query(u"Barcode:", 'number')
        if barcode is None:
            return
        if not self.dataman.verify_barcode(barcode):
            appuifw.note(u"Invalid barcode.", "error")
            return

        price = appuifw.query(u"Price:", 'float')
        if not price:
            return

        description = appuifw.query(u"Description (optional):", 'text')
        if description is None:
            description = u""

        prices = self.dataman.get_prices(barcode, price, description)
        if not prices:
            appuifw.note(u'No prices for code %s' % (barcode,), 'info')

        self.refresh_results_lb(self.get_results_list(prices, barcode))

    def refresh(self):
        confirm = appuifw.query(u"This will take a long time and requires data transfer. Confirm?", 'query')
        if not confirm:
            return

        self.dataman.refresh()
        self.load_settings_list()
        self.refresh_settings_lb()
        self.refresh_results_lb(self.get_results_list([]))

    def confirm_exit(self):
        self.dataman.close()
        return True

    def menu_about(self):
        self.about_dialog(
            name=u"GoMarket",
            version=u"0.1",
            year=u'2009',
            authors=[ u"Osvaldo Santana Neto", u"Ramiro Luz" ],
            icon="E:\\Python\\icon.png",
            license=u"MIT License",
        )



def main():
    app = MainApp()
    app.run()


if __name__ == '__main__':
    main()
