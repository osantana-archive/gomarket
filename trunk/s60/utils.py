# -*- coding: utf-8 -*-
# 
#  utils.py
#  comprices
#  
#  Created by Osvaldo Santana on 2009-02-27.
#  Copyright 2009 Triveos Tecnologia Ltda. All rights reserved.
# 

# http://www.pythonbrasil.com.br/moin.cgi/CodigoBarras
class InvalidBarcode(Exception):
    pass

def compute_barcode_checksum(arg):
    weight = [1, 3] * 6
    magic = 10
    sum_ = 0

    for i in range(12):
        sum_ += int(arg[i]) * weight[i]
    digit = (magic - (sum_ % magic)) % magic
    if digit < 0 or digit >= magic:
        raise InvalidBarcode("Error validating barcode.")
    return digit

def verify_barcode(bits):
    if len(bits) != 13:
        return False
    computed_checksum = compute_barcode_checksum(bits[:12])
    
    if computed_checksum == 10:
        computed_checksum = "X"
    else:
        computed_checksum = str(computed_checksum)
        
    codebar_checksum = bits[12]
    if codebar_checksum != computed_checksum:
        return False
    return True
