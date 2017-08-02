# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Authors: Ian Li <ian.li@elico-corp.com> and Eric Caudal <eric.caudal@elico-corp.com>
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


{
    'name': 'Stock Back-to-back orders',
    'version': '0.1',
    'category': 'Warehouse',
    'description': """
This module aims to change the original back-order logic of OpenERP in chained locations introducing true back-to-back orders.

STANDARD OPENERP BACK-TO-BACK ORDER BEHAVIOR:
Original behavior is not fully suitable to handle back-to-back backorders process (check "back-to-back orders comparison.pdf"):
eg: Let's take the following example to understand the implemented difference:
- One PO from a supplier for the full quantity (eg 100 PCE) and your supplier ships immediately only the available quantity which is 70 PCE. 
- 30 PCE are to be shipped later on.
- Setup with following chained location: SUPPLIER => TRANSIT (Chained/Manual) => INPUT locations 

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is processed and shipped for 70 PCE (done state)
- DN2 is kept with 100 PCE (in waiting state "waiting that all replenishments arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT) as back order of DN1.

Several drawbacks make current behavior unappropriate:
- Stock in the different locations are not reflecting real stocks.
- This is due to the fact that original delivery note is kept in waiting state in input or output location until all incoming chained DN are processed. 
- For this reason as well, real stock in the warehouse is incorrect in our case and is only correct when all backorders are shipped impacting company stock visibility.
- Documents (DN) are not following actual flow (one document missing)

ENHANCED BACK-TO-BACK ORDER BEHAVIOR
This modules replace standard OpenERP behavior by an enhanced back-to-back order workflow with the following behavior:
- Within a chained location structure, all chained moves will be created for the full quantity (eg: 100 PCE), following standard OE behavior.
(for how many chained location that has been created: if a second location is chained, an additional chained move is created)
- Nevertheless, when a partial quantity is shipped in the original delivery note (eg: 70 PCE), all related chained moves are updated with this new quantity 
(70 PCES) for as many level as necessary (difference with standard behavior).
- Backorders and related chained moves are created with the remaining quantities (eg: 30 PCE)
- Automated and manual chained behavior are respected.

Taking back our previous example (check as well "back-to-back orders comparison.pdf"):

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is shipped to 70 PCE (done state)
- DN2 is kept with 100 PCE (in waiting state "waiting that all replenishments arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT)

When DN1 is partially shipped with 70 PCE:
- DN2 quantity is changed to 70 PCE (and depending on stock marked as available since in our example it is set as manual). 
If automatic chained move, it would be automatically shipped according to DN1 shipment.
- a back order DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT), 
- chained move DN4 is automatically created with 30 PCE (from TRANSIT to INPUT)

Please note:
- In this case, workflow is closer to reality: all real stocks figures are correct and all relevant documents are created.
- Later on, DN2 and DN4 can be shipped separately (as they are setup as manual in this example)
- As many back order as necessary can be created: all chained moves are automatically updated and created accordingly
- this behavior works as well in case of sales orders.

Hereafter are the modifications that are applied to original module:
- Added internal move memory type;
- Changed criteria of picking type;
- Added a field to trace the chained picking;
- Changed back order logic;
- Overrode the default workflow of procurement (rely on the new next_move filed of stock.move) ;   
- Updated Picked Rate calculate function;
- Updating procurement.move_id for new moves of backorder.

TODO:
This module introduces a regression as original backorder behavior is not available anymore. 
This module is in principle not compatible with automatic procurement and scheduler.
Best would be to integrate this behavior in standard stock module in order to have this behavior and original behavior (with a new "back-to-back" chained location type)
""",
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn/',
    'depends': ['sale', 'stock', 'procurement', 'purchase'],
    "category" : "Generic Modules/Inventory Control",
    'init_xml': [],
    'update_xml': [
		'wizard/stock_partial_move_view.xml',
        'stock_workflow_backorder.xml',
        'stock_view.xml'
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
