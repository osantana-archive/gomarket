#!/usr/bin/env python
# -*- coding=utf-8 -*-

import sys
import csv
import urllib

servidor = 'http://localhost'
#servidor = 'http://192.168.1.105'
#servidor = 'http://comprices.appspot.com'
porta = '8080'
endereco_base = '%s:%s' % (servidor,porta)
#endereco_base = '%s' % servidor
url_pais = '%s/country/%%s/' % endereco_base
url_estado = '%s/state?%%s' % endereco_base
url_cidade = '%s/city?%%s' % endereco_base

f_estados = file('estados.csv')
f_cidades = file('cidades.csv')
f_cidades = file('capitais.csv')
csvr_estados = csv.reader(f_estados)
csvr_cidades = csv.reader(f_cidades)
l_paises = ['Brazil','USA']
l_estados = []
l_cidades = []

for row in csvr_estados:
    l_estados.append(row)

for row in csvr_cidades:
    l_cidades.append(row)

urls_pais = []
for i in l_paises:
    urls_pais.append( url_pais % i )

urls_estados = []
for i in l_estados:
    urls_estados.append( url_estado % (urllib.urlencode({'parent_name':i[1],
                                                         'name':i[0]})))

urls_cidades = []
for i in l_cidades:
    urls_cidades.append( url_cidade % (urllib.urlencode({'parent_name':i[1],
                                                         'name':i[0]})))
for i in urls_pais:
    s = urllib.urlopen(i).read()
    print i, s

for i in urls_estados:
    s = urllib.urlopen(i).read()
    print i, s

for i in urls_cidades:
    s = urllib.urlopen(i).read()
    print i, s

i = "%s/store?parent_name=Curitiba&name=DIP&address=Rua" % endereco_base
s = urllib.urlopen(i).read()
print i, s
