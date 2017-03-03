# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Siyuan Gu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name': 'Excel report for Mrp Production',
 'version': '0.1',
 'category': '',
 'depends': ['mrp_production_workcenter_line_reporting',
             'report_xls'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Excel report for Mrp Production
===================================
This module allows you to export excel report for Mrp Production
with speific category during one specific period.

Usage
-----


Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com
""",
 'images': [],
 'demo': [],
 'data': ['wizard/report_quantity.xml',
          'wizard/report_scraped.xml',
          'report/report_quantity.xml',
          'report/report_scraped.xml'],
 'test': [],
 'installable': True,
 'application': False}
