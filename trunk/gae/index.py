#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

class Address(db.Model):
    description = db.StringProperty()
    city = db.ReferenceProperty(City)

class AddressForm(djangoforms.ModelForm):
    class Meta:
        model = Address

class Market(db.Model):
    name = db.StringProperty()
    address = db.ReferenceProperty(Address)

class MarketForm(djangoforms.ModelForm):
    class Meta:
        model = Market

class Product(db.Model):
    description = db.StringProperty()
    price = db.FloatProperty()
    market = db.ReferenceProperty(Market)

class ProductForm(djangoforms.ModelForm):
    class Meta:
        model = Product

# Functions used in various handlers.
def getByName(self, *args, **kwargs):
    name = kwargs.get('name')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('name=',name)
    result = q.fetch(1)
    return result

def getByKey(self, *args, **kwargs):
    key = kwargs.get('key')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.get(key)
    result = q.fetch(1)
    return result

def getByDescription(self, *args, **kwargs):
    description = kwargs.get('description')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('description=',description)
    result = q.fetch(1)
    return result

def getByAbbreviation(self, *args, **kwargs):
    abbreviation = kwargs.get('abbreviation')
    modelClass = kwargs.get('modelClass')
    q = modelClass.all()
    q.filter('abbreviation=',abbreviation)
    result = q.fetch(1)
    return result

def newCountry(self, *args, **kwargs):
    name = kwargs.get("name")
    abbreviation = kwargs.get("abbreviation")
    ean13_prefix = kwargs.get("ean13_prefix")
    country = Country(name=name,
                      abbreviation=abbreviation,
                      ean13_prefix=ean13_prefix,
                      )
    db.put(country)
    return country

def newState(self, *args, **kwargs):
    name = kwargs.get("name")
    abbreviation = kwargs.get("abbreviation")
    country = kwargs.get("country")
    state = State(name=name,
                  abbreviation=abbreviation,
                  ean13_prefix,
                 )
    db.put(state)
    return state

def newCity(self, *args, **kwargs):
    name = kwargs.get("name")
    state = kwargs.get("state")
    city = City(name=name,
                state=state,
               )
    db.put(city)
    return city

def newAddress(self, *args, **kwargs):
    description = kwargs.get("description")
    city = kwargs.get("city")
    address = Address(description=description,
                      city=city,
                     )
    db.put(address)
    return address

def newMarket(self, *args, **kwargs):
    name = kwargs.get("name")
    address = kwargs.get("address")
    m = Market(
        name=name,
        address=address,
    )
    db.put(m)
    return m

def newProduct(self, *args, **kwargs):
    description = kwargs.get('description')
    price = kwargs.get('price')
    market = kwargs.get('market')
    p = Product(
            description=description,
            price=price,
            market=market)
    db.put(p)
    return p

#----------------------------------------------------------------------------#
# Request Handlers.
class HandleIndex(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<H1>GoMarket is used for Nokia S60 devices!!</H1>')

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
 
class HandleAddress(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        name = self.request.get("name")
        address = None
        if key:
            address = db.get(key)
        elif name:
            address = getByName(name=name,
                                modelClass=Address)
        if address:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(address))
        else:
            error(404)

    def post(self):
        data = AddressForm(data=self.request.POST)
        if data.is_valid():
            model_object = data.save(commit=False)
            model_object.put()
            self.redirect('/')
        else:
            error(200)
 
class HandleMarket(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        name = self.request.get("name")
        market = None
        if key:
            market = db.get(key)
        elif name:
            market = getByName(name=name,
                               modelClass=Market)
        if market:
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(simplejson.dumps(market))
        else:
            error(404)

    def post(self):
        data = MarketForm(data=self.request.POST)
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
 
application = webapp.WSGIApplication(
                                     [('/', HandleIndex),
                                      ('^country/', HandleCountry),
                                      ('^state/', HandleState),
                                      ('^city/', HandleCity),
                                      ('^address/', HandleAddress),
                                      ('^market/', HandleMarket),
                                      ('^product/', HandleProduct),
                                      ],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

