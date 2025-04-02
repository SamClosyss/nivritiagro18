{
    'name': 'Disable Create and Edit on Many2one',
    'summary': 'Disable to Create and Edit on Many2one Field.'
               'Or you can enable by changing user setting.',
    'description': 'Prevent staff to create and edit Many2one Field.'
                   'If you want to create and edit Many2one Field then change user setting',
    'author': "Sonny Huynh",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale'],

    'data': [
        'security/create_edit_many2one_group.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'disable_create_edit_many2one/static/src/js/*.js',
        ],
    },

    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'images': [
        'static/description/banner.png',
    ],
    'license': 'OPL-1',
    'price': 30.00,
    'currency': 'EUR',
}