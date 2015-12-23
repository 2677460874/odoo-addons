# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock PMC Report',
    'version': '1.0',
    'category': '',
    # depends sale_extra is_draft field,
    'depends': [
        'sale_extra',
        'purchase',
        'stock',
    ],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'stock_view.xml',
        'wizard/stock_inventory_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
