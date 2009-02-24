#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import md5
sys.path.append("E:\\Python")

import e32dbm

from skel import *

APP_NAME = u"gomarket"
APP_VERSION = u"0.1"
RESOURCE_DIR = "E:\\Python"

COUNTRIES_TEST = {
    u'key_a': u'Brazil',
    u'key_b': u'USA',
}
STATES_TEST = {
    u'key_a': {
        u'key_aa': u'Sao Paulo',
        u'key_ab': u'Rio de Janeiro',
    },
    u'key_b': {
        u'key_ba': u'Florida',
        u'key_bb': u'Alabama',
    },
}
CITIES_TEST = {
    u'key_aa': {
        u'key_aaa': u'Sao Paulo',
        u'key_aab': u'Sao Jose do Rio Preto',
    },
    u'key_ab': {
        u'key_aba': u'Rio de Janeiro',
        u'key_abb': u'Niteroi',
    },
    u'key_ba': {
        u'key_baa': u'Miami',
        u'key_bab': u'Orlando',
    },
    u'key_bb': {
        u'key_bba': u'Montgomery',
        u'key_bbb': u'Jackson',
    },
}

STORES_TEST = {
    u'key_aaa': {
        u'key_aaaa': u'Supermercado Extra Jaguare\nRua Foo',
        u'key_aaab': u'Supermercado Extra Pinheiros\nRua Bar',
    },
}

PRICES_TEST = {
    u'key_aaab': {
        u'978': '10.90',
    },
}


class DataManager(object):
    def __init__(self, resourcedir):
        self.resourcedir = resourcedir

        self.config = e32dbm.open(os.path.join(self.resourcedir, 'config.db'), 'nf')
        self._cache_countries = e32dbm.open(os.path.join(self.resourcedir, 'countries.db'), 'nf')
        # self._cache_ean_prefix = e32dbm.open(os.path.join(self.resourcedir, 'eanprefix.db'), 'nf')
        self._cache_states = e32dbm.open(os.path.join(self.resourcedir, 'states.db'), 'nf')
        self._cache_cities = e32dbm.open(os.path.join(self.resourcedir, 'cities.db'), 'nf')
        self._cache_stores = e32dbm.open(os.path.join(self.resourcedir, 'stores.db'), 'nf')

    # country
    def set_country(self, country):
        self.config[u'country'] = country
        self.state = u''
        self.city = u''
        self.store = u''
        self._cache_states.clear()
        self._cache_cities.clear()
        self._cache_stores.clear()
        self._cache_states.sync()
        self._cache_cities.sync()
        self._cache_stores.sync()
    def get_country(self):
        if not self.config.has_key(u'country'):
            self.config[u'country'] = u''
        return self.config[u'country']
    country = property(get_country, set_country)

    def get_country_name(self):
        if not self._cache_countries.has_key(self.country):
            return u''
        return unicode(self._cache_countries[self.country])
    country_name = property(get_country_name)

    def _request_countries(self):
        # TODO: urllib...
        print 'Getting country list...'
        return COUNTRIES_TEST
    def add_country(self, name):
        # TODO: urllib post and get new key...
        key = md5.md5(name).hexdigest()
        COUNTRIES_TEST[unicode(key)] = unicode(name)
        self._cache_countries[unicode(key)] = unicode(name)
        return key

    def countries(self):
        if not len(self._cache_countries):
            self._cache_countries.update(self._request_countries())
            self._cache_countries.sync()
        country_list = [ (unicode(k), unicode(v)) for k,v in self._cache_countries.items() ]
        country_list.sort(lambda x,y: cmp(x[1],y[1]))
        return country_list

    # state
    def set_state(self, state):
        self.config[u'state'] = state
        self.city = u''
        self.store = u''
        self._cache_cities.clear()
        self._cache_stores.clear()
        self._cache_cities.sync()
        self._cache_stores.sync()
    def get_state(self):
        if not self.config.has_key(u'state'):
            self.config[u'state'] = u''
        return self.config[u'state']
    state = property(get_state, set_state)

    def get_state_name(self):
        if not self._cache_states.has_key(self.state):
            return u''
        return unicode(self._cache_states[self.state])
    state_name = property(get_state_name)

    def _request_states(self, country):
        # TODO: urllib...
        print 'Getting state list of %s...' % (country,)
        return STATES_TEST[country]
    def add_state(self, name):
        # TODO: urllib post and get new key...
        key = md5.md5(name).hexdigest()
        STATES_TEST[self.country][unicode(key)] = unicode(name)
        self._cache_states[unicode(key)] = unicode(name)
        return key

    def states(self):
        country = self.country
        if not len(self._cache_states):
            self._cache_states.update(self._request_states(country))
            self._cache_states.sync()
        state_list = [ (unicode(k), unicode(v)) for k,v in self._cache_states.items() ]
        state_list.sort(lambda x,y: cmp(x[1],y[1]))
        return state_list

    # city
    def set_city(self, city):
        self.config[u'city'] = city
        self.store = u''
        self._cache_stores.clear()
        self._cache_stores.sync()
    def get_city(self):
        if not self.config.has_key(u'city'):
            self.config[u'city'] = u''
        return self.config[u'city']
    city = property(get_city, set_city)

    def get_city_name(self):
        if not self._cache_cities.has_key(self.city):
            return u''
        return unicode(self._cache_cities[self.city])
    city_name = property(get_city_name)

    def _request_cities(self, state):
        # TODO: urllib...
        print 'Getting city list...'
        return CITIES_TEST[state]
    def add_city(self, name):
        # TODO: urllib post and get new key...
        key = md5.md5(name).hexdigest()
        CITIES_TEST[unicode(key)] = unicode(name)
        self._cache_cities[unicode(key)] = unicode(name)
        return key

    def cities(self):
        state = self.state
        if not len(self._cache_cities):
            self._cache_cities.update(self._request_cities(state))
            self._cache_cities.sync()
        city_list = [ (unicode(k), unicode(v)) for k,v in self._cache_cities.items() ]
        city_list.sort(lambda x,y: cmp(x[1],y[1]))
        return city_list

    # store
    def set_store(self, store):
        self.config[u'store'] = store
    def get_store(self):
        if not self.config.has_key(u'store'):
            self.config[u'store'] = u''
        return self.config[u'store']
    store = property(get_store, set_store)

    def get_store_name(self):
        if not self._cache_stores.has_key(self.store):
            return u''
        return unicode(self._cache_stores[self.store].split('\n')[0])
        
    def get_store_address(self):
        if not self._cache_stores.has_key(self.store):
            return u''
        try:
            return unicode(self._cache_stores[self.store].split('\n')[1])
        except IndexError:
            return u''
            
    def _request_stores(self, city):
        # TODO: urllib...
        print 'Getting store list...'
        return STORES_TEST[city]
    def add_store(self, name, address):
        # TODO: urllib post and get new key...
        key = md5.md5(name).hexdigest()
        value = unicode(name) + u'\n' + unicode(address)
        STORES_TEST[unicode(key)] = value
        self._cache_stores[unicode(key)] = value
        return key
        
    def stores(self):
        city = self.city
        if not len(self._cache_stores):
            self._cache_stores.update(self._request_stores(city))
            self._cache_stores.sync()

        ret = []
        for k, v in self._cache_stores.items():
            name, address = v.split("\n")
            ret.append( (unicode(k), unicode(name), unicode(address)) )
        ret.sort(lambda x,y: cmp(x[1],y[1]))

        return ret

    def _get_store_name(self):
        return self._cache_stores[self.config[u'store']]
    store_name = property(_get_store_name)


    # def get_ean13_prefix(self):
    #     return self._ean_prefix[self.config['country']]

    def close(self):
        self.config.close()
        self._cache_countries.close()
        # self._cache_ean_prefix.close()
        self._cache_states.close()
        self._cache_cities.close()
        self._cache_stores.close()

    def refresh(self):
        # TODO
        pass

    def get_prices(self, barcode, price, description):
        # TODO
        if barcode == 978:
            return [
                (u'Supermercado Foo', u'R$10,00'),
                (u'Supermercado Bar', u'R$10,00'),
                (u'Supermercado Baz', u'R$10,00'),
            ]
        else:
            return []




class MainApp(AppSkel):
    """This is the Application class"""

    TAB_SETTINGS = 0
    TAB_STORES = 1
    TAB_RESULTS = 2

    SETTING_COUNTRY = 0
    SETTING_STATE = 1
    SETTING_CITY = 2

    def init(self):
        self.title = u"GoMarket"
        self.datamanager = DataManager(RESOURCE_DIR)

        self.settings_lb = None
        self.stores_lb = None
        self.results_lb = None

    def setup(self):
        start_tab = self.TAB_SETTINGS
        if self.datamanager.city:
            start_tab = self.TAB_STORES
        if self.datamanager.store:
            start_tab = self.TAB_RESULTS
        self.activate_tab(start_tab)

    def tabs(self):
        return (
            (u'Settings', self.tab_settings_body),
            (u'Stores', self.tab_stores_body),
            (u'Result', self.tab_results_body, self.tab_results_menu),
        )

    def menu(self):
        return [
            (u'Refresh', self.refresh),
        ]


    # TAB_SETTINGS
    def tab_settings_body(self):
        self.settings_list = [
            (u'Country', self.datamanager.country_name),
            (u'State', self.datamanager.state),
            (u'City', self.datamanager.city),
        ]
        self.settings_lb = appuifw.Listbox(self.settings_list, self.tab_callback_settings)
        return self.settings_lb

    def tab_callback_settings(self):
        index = self.settings_lb.current()
        dataman = self.datamanager

        if index == self.SETTING_COUNTRY:
            self._setting('country',
                dataman.countries,
                dataman.get_country_name,
                dataman.set_country,
                dataman.add_country,
                [ self.SETTING_STATE, self.SETTING_CITY ]
            )
        elif index == self.SETTING_STATE:
            self._setting('state',
                dataman.states,
                dataman.get_state_name,
                dataman.set_state,
                dataman.add_state,
                [ self.SETTING_CITY ]
            )
        else:
            self._setting('city',
                dataman.cities,
                dataman.get_city_name,
                dataman.set_city,
                dataman.add_city,
                [ ]
            )
            if dataman.city:
                self.activate_tab(self.TAB_STORES)
            
    def _setting(self, option, datasrc, get_name, set_attr, add_item, reset_list):
        index = self.settings_lb.current()
        option_keys = [None]
        option_values = [u'NEW']
        try:
            for key, value in datasrc():
                option_keys.append(key)
                option_values.append(value)
        except KeyError:
            pass # only NEW option
            
        selection = appuifw.selection_list(option_values, 1)
        if selection is None:
            return
        key = option_keys[selection]
        value = option_values[selection]

        if key is None:
            value = appuifw.query(u"New %s" % (option,), 'text')
            if value is None:
                return
            key = add_item(value)

        set_attr(key)
        
        # reset next options
        self.settings_list[index] = (self.settings_list[index][0], get_name())
        for reset in reset_list:
            self.settings_list[reset] = (self.settings_list[reset][0], u'')
        self.settings_lb.set_list(self.settings_list, index)
    # /TAB_SETTINGS


    # TAB_STORES
    def tab_stores_body(self):
        self.load_stores_list()
        self.stores_lb = appuifw.Listbox(self.store_items, self.tab_callback_stores)
        return self.stores_lb

    def tab_callback_stores(self):
        index = self.stores_lb.current()

        if self.store_keys[index] is None:
            try:
                name, address = appuifw.multi_query(u'Store Name:', u'Address:')
            except TypeError: # cancel
                return
            if not name.strip():
                return

            key = self.datamanager.add_store(name, address)

            self.load_stores_list()
            self.refresh_stores_lb()
        else:
            self.datamanager.config['store'] = self.store_keys[index]

        # move to result if it already exists
        if self.results_lb:
            result_list = self.get_results_list([])
            self.refresh_results_lb(result_list)
        self.activate_tab(self.TAB_RESULTS)

    def load_stores_list(self):
        self.store_keys = [None]
        self.store_items = [ (u"NEW", u"") ]
        for key, name, address in self.datamanager.stores():
            self.store_keys.append(key)
            self.store_items.append( (name, address) )

    def refresh_stores_lb(self):
        self.stores_lb.set_list(self.store_items)
    # /TAB_STORES


    # TAB_RESULTS
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
        if barcode:
            results_list = [ (u'Get Price', u"%s / %s" % (self.datamanager.store_name, barcode)) ]
        else:
            results_list = [ (u'Get Price', self.datamanager.store_name) ]
        results_list += results
        return results_list

    def refresh_results_lb(self, results):
        self.results_lb.set_list(results)
    # /TAB_RESULTS


    # handle callbacks...
    def get_prices(self):
        if not self.datamanager.config['store']:
            appuifw.note(u"You need to select a store.", "error")
            self.activate_tab(self.TAB_STORES)
            return

        barcode = appuifw.query(u"Barcode:", 'number') #, self.datamanager.get_ean13_prefix())
        if barcode is None:
            return
        price = appuifw.query(u"Price:", 'float')
        if not price:
            return

        description = appuifw.query(u"Description (optional):", 'text')
        if description is None:
            description = u""

        prices = self.datamanager.get_prices(barcode, price, description)
        if not prices:
            appuifw.note(u'No prices for code %s' % (barcode,), 'info')
        results = self.get_results_list(prices, barcode)
        self.refresh_results_lb(results)

    def refresh(self):
        self.datamanager.refresh()

    def confirm_exit(self):
        self.datamanager.close()
        return True
    def menu_about(self):
        self.about_dialog(
            name=u"GoMarket",
            version=u"0.1",
            year=u'2009',
            authors=[ u"Osvaldo Santana Neto", u"Ramiro Luz" ],
            icon="E:\\Python\\gomarket_icon.png",
            license=u"MIT License",
        )

def main():
    app = MainApp()
    app.run()

if __name__ == '__main__':
	main()
