# -*- coding: utf-8 -*-

{
    "name" : "Manual Currency Exchange Rate on Invoice/Payment/Sale/Purchase in Odoo",
    # "version" : "17.0.0.0",
    "depends" : ['base','account','purchase','sale_management','stock'],
    "author": "Closyss",
    "summary": "Apps apply manual currency rate on invoice manual currency rate on payment manual currency rate on sales manual currency rate on purchase custom currency rate on invoice manual Currency Exchange Rate on Invoice custom Currency Exchange Rate on sales order",
    "description": "",
    "price": 22,
    "currency": "EUR",
    'category': 'Accounting',
    "website" : "https://www.closyss.com",
    "data" :[
             "views/customer_invoice.xml",
             "views/account_payment_view.xml",
             "views/purchase_view.xml",
             "views/sale_view.xml",
        ],
    'qweb':[],
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}