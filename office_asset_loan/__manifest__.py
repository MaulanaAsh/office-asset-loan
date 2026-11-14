{
    'name': 'Office Asset Loan',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Record office assets and who borrows them',
    'author': 'Maulana Ash Shddiq',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/office_asset_loan_security.xml',
        'security/ir.model.access.csv',
        'data/office_asset_loan_sequence.xml',
        'views/office_asset_views.xml',
        'views/office_asset_loan_views.xml',
        'views/office_asset_menus.xml',
    ],
    'application': True,
    'installable': True,
}
