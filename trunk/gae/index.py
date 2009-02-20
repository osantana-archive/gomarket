from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Country(db.Model):
    name = db.StringProperty()
    abreviation = db.StringProperty()
    ean13_prefix = db.StringProperty()

class State(db.Model):
    name = db.StringProperty()
    abreviation = db.StringProperty()
    country = db.ReferenceProperty(Country)

class City(db.Model):
    name = db.StringProperty()
    state = db.ReferenceProperty(State)

class Address(db.Model):
    description = db.StringProperty()
    city = db.ReferenceProperty(City)

class Market(db.Model):
    name = db.StringProperty()
    address = db.ReferenceProperty(Address)

class Product(db.Model):
    description = db.StringProperty()
    price = db.FloatProperty()
    market = db.ReferenceProperty(Market)

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

def newCountry(self, *args, **kwargs):
    name = kwargs.get("name")
    abreviation = kwargs.get("abreviation")
    ean13_prefix = kwargs.get("ean13_prefix")
    country = Country(name=name,
                      abreviation=abreviation,
                      ean13_prefix=ean13_prefix,
                      )
    db.put(country)
    return country

def newState(self, *args, **kwargs):
    name = kwargs.get("name")
    abreviation = kwargs.get("abreviation")
    country = kwargs.get("country")
    state = State(name=name,
                  abreviation=abreviation,
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

#TODO: post, json, search, urls
#----------------------------------------------------------------------------#
# Request Handlres.
class HandleIndex(webapp.RequestHandler):
    def get(self):
        response.out.write('<H1>GoMarket is used for Nokia S60 devices!!</H1>')

class HandleAddress(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        address = db.get(key)
        response.out.write('"%s","%s","%s","%s","%s"' %
            address.description,
            address.city,
            address.state,
            address.ean13_prefix,
            address.country
        )


class HandleMarket(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")

        market = db.get(key)
        response.out.write('"%s","%s","%s","%s","%s","%s"' %
            market.name
            market.address.description,
            market.address.city,
            market.address.state,
            market.address.ean13_prefix,
            market.address.country
        )

class HandleProduct(webapp.RequestHandler):
    def get(self):
        key = self.request.get("key")
        product = db.get(key)

        response.out.write('"%s",%s,"%s"' % \
              (prod.market.name,
               prod.price,
               prod.description))


application = webapp.WSGIApplication(
                                     [('/', HandleIndex),],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

