#!/usr/bin/env python
# -*- coding=utf-8 -*-

'''
Requests:

GET
---
/countries/ - returns a JSON 'dict' with: { country_key: country_name }
/states/{country_key}/ - returns a JSON 'dict' with: { state_key: state_name }
/cities/{state_key}/ - returns a JSON 'dict' with: { city_key: city_name }
/stores/{city_key}/ - returns a JSON 'dict' with: { store_key: store_name + '\n'
+ store_address }

/prices/?barcode=XXXXXXXXXXX&price=X.XX&description=XXXXX -
Put this info in our database (validate barcode and price!=0) and returns a JSON
'list' with:
    [
        [ store_name1, price1 ],
        [ store_name2, price2 ],
        :
        [ store_nameN, priceN ],
   ]

ordered by price.


POST
----
/(countries|states|cities)/
    - send ->
        field: (country|state|city)_name 
        field: parent_key (ex. country_key to add a state or state_key to add
city)
    - response -> JSON string with the new (country|state|city) key
/stores/
    - send ->
        field: store_description with unicode(store_name + '\n' + store_address)
        field: parent_key (in this case the city_key)
    - response -> JSON string with the new store key

'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
import simplejson

class Country(db.Model):
    name = db.StringProperty()
    abbreviation = db.StringProperty()
    ean13_prefix = db.StringProperty()

class CountryForm(djangoforms.ModelForm):
    class Meta:
        model = Country

class State(db.Model):
    name = db.StringProperty()
    abbreviation = db.StringProperty()
    country = db.ReferenceProperty(Country)

class StateForm(djangoforms.ModelForm):
    class Meta:
        model = State

class City(db.Model):
    name = db.StringProperty()
    state = db.ReferenceProperty(State)

class CityForm(djangoforms.ModelForm):
    class Meta:
        model = City

class Store(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    city = db.ReferenceProperty(City)

class StoreForm(djangoforms.ModelForm):
    class Meta:
        model = Market

class Product(db.Model):
    description = db.StringProperty()
    barcode = db.StringProperty()
    price = db.FloatProperty()
    store = db.ReferenceProperty(Store)

class ProductForm(djangoforms.ModelForm):
    class Meta:
        model = Product

# Functions used in various handlers.
def getByName(*args, **kwargs):
    name = kwargs.get('name')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('name=',name)
    result = q.fetch(1)
    return result

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

def getByAbbreviation(*args, **kwargs):
    abbreviation = kwargs.get('abbreviation')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('abbreviation=',abbreviation)
    result = q.fetch(1)
    return result

def newCountry(*args, **kwargs):
    name = kwargs.get("name")
    abbreviation = kwargs.get("abbreviation")
    ean13_prefix = kwargs.get("ean13_prefix")
    country = Country(name=name,
                      abbreviation=abbreviation,
                      ean13_prefix=ean13_prefix,
                      )
    db.put(country)
    return country

def newState(*args, **kwargs):
    name = kwargs.get("name")
    abbreviation = kwargs.get("abbreviation")
    country_name = kwargs.get("country_name")
    country = getByName(name=country_name,
                        modelClass=Country)
    state = State(name=name,
                  abbreviation=abbreviation,
                  country=country,
                 )
    db.put(state)
    return state

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
    city_name = kwargs.get("city_name")
    city = getByName(name=city_name,
                     modelClass=City)
    m = Market(
        name=name,
        address=address,
        city=city
    )
    db.put(m)
    return m

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
        query.ancestor(Key(ancestor_key))
    results = query.fetch(limit=500)
    for r in results:
        response_data[r.key]=r.name
    return response_data

#----------------------------------------------------------------------------#
# Request Handlers.
class HandleIndex(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<H1>GoMarket is used for Nokia S60 devices!!</H1>')

class HandleCountries(webapp.RequestHandler):
    def get(self):
        countries = getResponseData(modelClass=Country)
        if countries:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(countries))
        else:
            error(404)

class HandleCountry(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        description = self.request.get("description")
        country = None
        if key:
            country = db.get(key)
        elif description:
            country = getByDescription(description=description,
                                       modelClass=Country)
        if country:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(country))
        else:
            error(404)

    def post(self):
        data = CountryForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)

class HandleStates(webapp.RequestHandler):
    def get(self):
        country_key = self.request.get('country_key')
        states = getResponseData(modelClass=States,
                                 ancestor_key=country_key)
        if states:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(states))
        else:
            error(404)

class HandleState(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        name = self.request.get("name")
        abbreviation = self.request.get("abbreviation")
        state = None
        if key:
            state = db.get(key)
        elif abbreviation:
            state = getByAbbreviation(abbreviation=abbreviation,
                                      modelClass=State)
        elif name:
            state = getByDescription(description=description,
                                     modelClass=State)
        if state:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(state))
        else:
            error(404)

    def post(self):
        data = StateForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)

class HandleCities(webapp.RequestHandler):
    def get(self):
        state_key = self.request.get('state_key')
        cities = getResponseData(modelClass=City,
                                 ancestor_key=state_key)
        if cities:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(cities))
        else:
            error(404)

class HandleCity(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        name = self.request.get("name")
        city = None
        if key:
            city = db.get(key)
        elif name:
            city = getByName(name=name,
                             modelClass=City)
        if city:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(city))
        else:
            error(404)

    def post(self):
        data = CityForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)

class HandleStores(webapp.RequestHandler):
    def get(self):
        city_key = self.request.get('city_key')
        response_data = {}
        query = Store.all()
        if city_key:
            query.ancestor(Key(city_key))

        results = query.fetch(limit=1000)
        for r in results:
            response_data[r.key] = '%s \n %s' % (r.name,r.address)

        if response_data:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(response_data))
        else:
            error(404)

class HandleStore(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        name = self.request.get("name")
        store = None
        if key:
            store = db.get(key)
        elif name:
            store = getByName(name=name,
                              modelClass=Store)
        if store:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(store))
        else:
            error(404)

    def post(self):
        data = StoreForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)
 
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
            self.response.write(simplejson.dumps(product))
        else:
            error(404)

    def post(self):
        data = ProductForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)

class HandlePrices(webapp.RequestHandler):
    def get(self):
        response_data = []
        barcode = self.request.get('barcode')
        price = self.request.get('price')
        description = self.request.get('description')
        store_key = self.request.get('store_key')
        # A very simple validation
        try:
            barcode = int(barcode)
        except:
            error(200)
        try:
            price = int(price)
        except:
            error(200)
        if barcode <=0 or price <= 0:
            error(200)

        # Put product information in the datastore.
        product = Product(
            description=description,
            barcode=barcode,
            price=price,
            store=Key(store_key)
        )
        db.put(product)

        # Find all(first 1000) prices for a product description.
        query = Product.all()
        query.order('-price')
        query.filter('description =',description)
        results = query.fetch(limit=1000)
        for p in results:
            response_data.append([p.store.name,p.price])

        if response_data:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(response_data))
        else:
            error(404)

application = webapp.WSGIApplication(
                                     [('/', HandleIndex),
                                      ('^country/', HandleCountry),
                                      ('^state/', HandleState),
                                      ('^city/', HandleCity),
                                      ('^address/', HandleAddress),
                                      ('^market/', HandleStore),
                                      ('^product/', HandleProduct),
                                      ('^countries/', HandleCountries),
                                      ('^states/{country_key}/', HandleStates),
                                      ('^cities/{state_key}/', HandleCities),
                                      ('^stores/{city_key}/', HandleStores),
                                      ('^prices/.*', HandlePrices),
                                      ],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

