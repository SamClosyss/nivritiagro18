{
    'name': 'Nivriti Broker',
    'author': 'Closyss Technologies',
    'depends': ['account', 'stock','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/account.xml',
        'views/stock.xml',
        'views/product.xml',
        'views/mrp.xml',
        'wizard/product_enquiry.xml',
        'wizard/stock_location_wiz.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
