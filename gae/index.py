from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Address(db.Model):
    description = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    ean13_prefix = db.StringProperty()
    country = db.StringProperty()

class Market(db.Model):
    name = db.StringProperty()
    address = db.ReferenceProperty(Address)

class Product(db.Model):
    description = db.StringProperty()
    price = db.FloatProperty()
    market = db.ReferenceProperty(Market)

# Functions used in various handlers.
def getAddress(self, *args, **kwargs):
    description = kwargs.get('description')
    qAddress = Address.all()
    qAddress.filter('description=',description)
    a = qAddress.fetch(1)
    return a

def newAddress(self, *args, **kwargs):
    address_desc = kwargs.get("address_desc")
    address_city = kwargs.get("address_city")
    address_state = kwargs.get("address_state")
    address_ean13_prefix = kwargs.get("address_ean13_prefix")
    address_country = kwargs.get("address_country")
    address = Address(description=address_desc,
                      city=address_city,
                      state=address_state,
                      ean13_prefix=address_ean13_prefix,
                      country=address_country)
    return self.address

def getMarket(self, *args, **kwargs):
    market_name = kwargs.get('market_name')
    qMarket = Market.all()
    qMarket.filter('name=',market_name)
    m = qMarket.fetch(1)
    return m

def newMarket(self, *args, **kwargs):
    market_name = kwargs.get("market_name")
    address_desc = kwargs.get("address_desc")
    address_city = kwargs.get("address_city")
    address_state = kwargs.get("address_state")
    address_ean13 = kwargs.get("address_ean13")
    address_country = kwargs.get("address_country")
    address = self.getAddress(description=address_desc)
    if not address:
        address = self.newAddress(
            address_desc=address_desc,
            address_city=address_city,
            address_state=address_state,
            address_ean13_prefix=address_ean13_prefix,
            address_country=address_country
        )
    m = Market(
        name=market_name,
        address=address
    )
    return m

def newProduct(self, *args, **kwargs):
    market_name = kwargs.get('market_name')
    description = kwargs.get('description')
    price = kwargs.get('price')
    m = self.getMarket(market_name=market_name)
    p = Product(
            description=description,
            price=price,
            market=m)
    db.put(p)
    return p

#----------------------------------------------------------------------------#
# Request Handlres.
class HandleIndex(webapp.RequestHandler):
    def get(self):
        response.out.write('<H1>GoMarket is used for Nokia S60 devices!!</H1>')

class HandleAddress(webapp.RequestHandler):
    def get(self):
        description = self.request.get("description")
        address = getAddress(description=description)
        response.out.write('"%s","%s","%s","%s","%s"' %
            address.description,
            address.city,
            address.state,
            address.ean13_prefix,
            address.country
        )


class HandleMarket(webapp.RequestHandler):
    def get(self):
        market_name = self.request.get("market_name")

        market = getMarket(market_name=market_name)
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
        description = self.request.get("prod_description")
        price = self.request.get("prod_price")
        market_name = self.request.get("market_name")
        address_desc = self.request.get("address_desc")
        address_city = self.request.get("address_city")
        address_state = self.request.get("address_state")
        address_ean13_prefix = self.request.get("address_ean13_prefix")
        address_country = self.request.get("address_country")
        phone_imei = self.request.get("imei") # NOT USING YET. #TODO
        if address_desc:
            m = self.newMarket(market_name=market_name,
                              address_desc=address_desc,
                              address_city=address_city,
                              address_state=address_state,
                              address_ean13_prefix=address_ean13_prefix,
                              address_country=address_country)
        else:
            qProduct = Product.all()
            qProduct.filter('price=',price)
            qProduct.filter('description=',description)
            qProduct.filter('market.name',market_name)
            prod = qProduct.fetch(1)

        if not prod:
            prod = newProduct(market_name=market_name,
                              description=description,
                              price=price)

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

