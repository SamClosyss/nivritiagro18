
{
    'name': 'Sales & Purchase Register',
    'version': '18.0',
    'summary': 'Accounting Reports',
    'description': 'Partner Ledger Report',
    'author': 'Closyss Technologies',
    'maintainer': 'Closyss',
    'company': 'Closyss',
    'website': 'https://closyss.odoo.com/',
    'depends': ['base','account_reports','account'],
    'category': 'Accounting',
    'demo': [],
    'data': [
            'views/excel_register_report.xml',
            'security/ir.model.access.csv',

             ],
    'installable': True,
    'qweb': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
