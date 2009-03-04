#!/usr/bin/env python
# vim:ts=4:sw=4:et:si:ai:sm
# -*- coding=utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.utils import simplejson

class Country(db.Model):
    name = db.StringProperty()
    ean13_prefix = db.StringProperty()

    def get_by_name(self,name):
        return getByName(name=name, modelClass=Country)

class State(db.Model):
    name = db.StringProperty()
    country = db.ReferenceProperty(Country)
    def get_by_name(self,name):
        return getByName(name=name, modelClass=State)

class City(db.Model):
    name = db.StringProperty()
    state = db.ReferenceProperty(State)
    def get_by_name(self,name):
        return getByName(name=name, modelClass=City)

class Store(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    city = db.ReferenceProperty(City)

class Product(db.Model):
    description = db.StringProperty()
    barcode = db.IntegerProperty()
    price = db.FloatProperty()
    last_update = db.DateTimeProperty(auto_now=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    store = db.ReferenceProperty(Store)

# Functions used in various handlers.
def getByName(*args, **kwargs):
    name = kwargs.get('name')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('name =',name)
    result = q.fetch(limit=10)
    if result:
        return result[0]
    else:
        return None

def getByKey(*args, **kwargs):
    key = kwargs.get('key')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.get(key)
    result = q.fetch(1)
    return result

def getByDescription(*args, **kwargs):
    description = kwargs.get('description')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('description=',description)
    result = q.fetch(1)
    return result

def newCountry(*args, **kwargs):
    name = kwargs.get("name")
    ean13_prefix = kwargs.get("ean13_prefix")
    country = Country(name=name,
                      abbreviation=abbreviation,
                      ean13_prefix=ean13_prefix,
                      )
    db.put(country)
    return country

def newObject(*args, **kwargs):
    name = kwargs.get("name")
    parent_key = kwargs.get("parent_key")
    model_object = modelClass(
        parent=Key(parent_key),
        name = name,
    )
    db.put(model_object)
    return model_object.key()


def newState(*args, **kwargs):
    name = kwargs.get("name")
    parent_key = kwargs.get("parent_key")
    model_object = modelClass(
        parent=Key(parent_key),
        name = name,
    )
    db.put(model_object)
    return model_object.key()

def newCity(*args, **kwargs):
    name = kwargs.get("name")
    state_name = kwargs.get("state_name")
    state = getByName(name=state_name,
                      modelClass=State)
    city = City(name=name,
                state=state,
               )
    db.put(city)
    return city

def newStore(*args, **kwargs):
    name = kwargs.get("name")
    address = kwargs.get("address")
    parent_key = kwargs.get("parent_key")
    p = Product(
        parent=Key(parent_key),
        name=name,
        address=address,
    )
    db.put(p)
    return p.key()

def newProduct(*args, **kwargs):
    description = kwargs.get('description')
    barcode = kwargs.get('barcode')
    price = kwargs.get('price')
    store_name = kwargs.get('store_name')
    store = getByName(name=store_name,
                      modelClass=Store)
    p = Product(
            description=description,
            barcode=barcode,
            price=price,
            store=store)
    db.put(p)
    return p

def getResponseData(*args,**kwargs):
    modelClass = kwargs['modelClass']
    ancestor_key = kwargs.get('ancestor_key')
    response_data = {}
    query = modelClass.all()
    if ancestor_key:
        query.ancestor(ancestor_key)
    results = query.fetch(limit=500)
    for r in results:
        response_data['%s' % r.key()]=r.name
    return response_data

#----------------------------------------------------------------------------#
# Request Handlers.
class HandleTeste(webapp.RequestHandler):
    def get(self):
        #state = State.all()
        state = City.all()
        response_data = {}
        for state in state.fetch(1000):
            response_data['%s' % state.key()] = state.name
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(response_data))

class HandleCountry(webapp.RequestHandler):
    def get(self, name=None):
        if name:
            country = Country(name=name)
            db.put(country)
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(simplejson.dumps(' %s - %s' % (country.name, country.key())))
        else:
            self.error(400)

class HandleState(webapp.RequestHandler):
    def get(self):
        name = self.request.get('name')
        parent_name = self.request.get('parent_name')
        try:
            country = Country.all().filter("name =", parent_name).fetch(1)[0]
        except IndexError:
            return

        state = State(name=name)
        state.country = country
        db.put(state)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s' % state.key()))

class HandleCity(webapp.RequestHandler):
    def get(self):
        name = self.request.get('name')
        parent_name = self.request.get('parent_name')
        state = State.all().filter("name =", parent_name).fetch(1)[0]
        city = City(name=name)
        city.state = state
        db.put(city)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s' % city.key()))

class HandleStore(webapp.RequestHandler):
    def get(self):
        name = self.request.get('name')
        address = self.request.get('address')
        parent_name = self.request.get('parent_name')
        city = City.all().filter("name =", parent_name).fetch(1)[0]
        store = Store(name=name,address=address)
        store.city = city
        db.put(store)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s' % store.key()))


class HandleProduct(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        description = self.request.get("description")
        product = None
        if key:
            product = db.get(key)
        elif description:
            product = getByDescription(description=description,
                                       modelClass=Product)
        if product:
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(simplejson.dumps(product))
        else:
            self.error(404)


class HandleIndex(webapp.RequestHandler):
    def get(self):
        self.response.out.write('''<html>
    <title>Comprices - appengine</title>
    <body>
        <div id="about" align="center">
        <table border="0">
          <tr>
            <td width="420">
              <div id="banner" class="image" align="center"><img src="/static/banner.png" border="0" alternate="Comprices banner"></div>
              <p align="left">
                <b>ComPrices is used for Nokia S60 devices to compare product prices!!</b>
              </p>
              <p align="left">
                The project was first named gomarket, so you can find the source code in the google code website, <a href="http://code.google.com/p/gomarket">ComPrices Project Site</a>.</p>
              <p align="left">
                You can download the installer for S60, <a href="http://gomarket.googlecode.com/files/comprices_bundle.sis">with</a> or <a href="http://gomarket.googlecode.com/files/comprices.sis">without</a>(in this case, the python interpreter must be installed in your device).<br />
                If you want, there is a zip file with sources and the two installer above <a href="http://gomarket.googlecode.com/files/comprices.zip">here</a>. The full list off downloads is <a href="http://code.google.com/p/gomarket/downloads/list">here</a>.<br />
              </p>
            </td>
          </tr>
          <tr>
            <td>
              Package with sources, resources and SIS packages 761 KB. - [ <a href="http://gomarket.googlecode.com/files/comprices.zip">comprices.zip</a> ]
            </td>
          </tr>
          <tr>
            <td>
              ComPrices without Python 35.3 KB. - [ <a href="http://gomarket.googlecode.com/files/comprices.sis">comprices.sis</a> ]
            </td>
          </tr>
          <tr>
            <td>
              ComPrices Package with Python 607 KB - [ <a href="http://gomarket.googlecode.com/files/comprices_bundle.sis">comprices_bundle.sis</a> ]
            </td>
          </tr>
        </table>
        </div>
    </body>
</html>
''')

class HandleCountries(webapp.RequestHandler):
    def get(self):
        countries = getResponseData(modelClass=Country)
        if countries:
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(simplejson.dumps(countries))
        else:
            self.error(404)

    def post(self):
        name = self.request.get('name')
        country = Country(
            name=name,
        )
        db.put(country)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s' % country.key()))

class HandleStates(webapp.RequestHandler):
    def get(self):
        country_key = self.request.get('key')
        if not country_key:
            self.error(400)

        country = Country.get(country_key)
        if not country:
            self.error(404)

        response_data = {}
        for state in country.state_set:
            response_data['%s' % state.key()] = state.name
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(response_data))

    def post(self):
        name = self.request.get('name')
        key = self.request.get('key')
        state = State(
            name=name,
        )
        country = Country.get(key)
        if not country:
            self.error(400)
        state.country = country

        db.put(state)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s'%state.key()))

class HandleCities(webapp.RequestHandler):
    def get(self):
        state_key = self.request.get('key')
        if not state_key:
            self.error(400)

        state = State.get(state_key)
        if not state:
            self.error(404)

        response_data = {}
        for city in state.city_set:
            response_data['%s' % city.key()] = city.name

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(response_data))

    def post(self):
        name = self.request.get('name')
        key = self.request.get('key')
        city = City(
            name=name,
        )
        state = State.get(key)
        if not state:
            self.error(400)
        city.state = state

        db.put(city)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s'%city.key()))

class HandleStores(webapp.RequestHandler):
    def get(self):
        city_key = self.request.get('key')
        if not city_key:
            self.error(400)
        city = City.get(city_key)
        if not city:
            self.error(404)
        response_data = {}
        for store in city.store_set:
            response_data['%s' % store.key()] = '%s \n %s' % (store.name,store.address)

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(response_data))

    def post(self):
        description = self.request.get('name')
        name, address = description.split('\n')
        key = self.request.get('key')
        store = Store(
            name=name,
            address=address,
        )
        city = City.get(key)
        if not city:
            self.error(400)
        store.city = city

        db.put(store)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps('%s' % store.key()))


class HandlePrices(webapp.RequestHandler):
    def get(self):
        barcode = self.request.get('barcode')
        price = self.request.get('price')
        description = self.request.get('description')
        store_key = self.request.get('key')
        # A very simple validation
        try:
            barcode = int(barcode)
        except:
            self.error(400)
        try:
            price = float(price)
        except:
            self.error(400)
        if barcode <=0 or price <= 0:
            self.error(400)

        store = Store.get(store_key)
        if not store:
            self.error(400)

        # Put product information in the datastore.
        product = Product(
            description=description,
            barcode=barcode,
            price=price,
        )
        product.store = store
        db.put(product)
        
        # Search prices based on the barcode and the city(store city) sent by the client.
        store_set = store.city.store_set
        store_keys = []
        for store in store_set:
            store_keys.append(store.key())
        product_query = Product.all()
        product_query.filter('store IN', store_keys)
        product_query.filter('barcode =',barcode)
        product_query.order('price')
        product_set = product_query.fetch(50)
        response_data = []
        for product in product_set:
            response_data.append(('%s\n%s' % (product.store.name,
                                              product.store.address), 
                                  unicode(product.price)))
        if not response_data:
            self.error(404)

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(simplejson.dumps(response_data))

application = webapp.WSGIApplication(
                                     [('/$', HandleIndex),
#                                      ('/country/(.*)/', HandleCountry),
#                                      ('/state/?', HandleState),
#                                      ('/teste/?', HandleTeste),
#                                      ('/city/?', HandleCity),
#                                      ('/store/?', HandleStore),
                                      ('/countries/?', HandleCountries),
                                      ('/states/?', HandleStates),
                                      ('/cities/?', HandleCities),
                                      ('/stores/?', HandleStores),
                                      ('/prices/?', HandlePrices),
                                      ],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

