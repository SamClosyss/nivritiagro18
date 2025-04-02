# -*- coding: utf-8 -*-
{
    'name' : 'Disable Form',
    # 'version' : '16.0',
    'summary': 'Disable form view using OWL',
    'sequence': -1,
    'description':"""
    Disable form view from ir.ui.view, from actions context,
    and from javascript using OWL.
    """,
    'category': 'Hidden',
    'depends' : ['web', 'sale'],
    'data': [
        'data/groups.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web.assets_backend': [
            # 'disable_form/static/src/components/*'
        ]
    },
    'license': 'LGPL-3',
    # 'price': 30.00,
    # 'currency': 'EUR',

}