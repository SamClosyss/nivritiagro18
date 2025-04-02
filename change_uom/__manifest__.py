# -*- coding: utf-8 -*-
###############################################################################
#
# Closyss Technologies Pvt. Ltd.
# Copyright (C) Closyss Technologies Pvt. Ltd.(<https://closyss.com>).
#
###############################################################################

{
    "name": 'Change-UOM',
    'category': 'UOM',
    'summary': 'User can forcefully change uom and any product at anytime & it will reflect evrywhere in line items',
    # "version": "17.0.0.1.0",
    "price": 10,
    'currency': 'USD',
    'description': """
    Some time we require to change product uom after it had already used in SO lines item or PO lines or invoice lines 
    etc at that time this module will help you to force fully change the uom.
""",
    "author": "Closyss Technologies Pvt. Ltd",
    'website': 'https://closyss.com',
    'depends': ['base', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/change_uom.xml',
        'views/product_temp.xml',
    ],
    "maintainer": "Closyss Technologies Pvt. Ltd",
    "support": "info@closyss.com",
    "images": ['static/description/uom_icon.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
