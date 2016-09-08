# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class res_partner(osv.osv):
    _inherit = 'res.partner'

    # _columns = {
    #     'property_account_prepayable': fields.property(
    #         'account.account',
    #         type='many2one',
    #         relation='account.account',
    #         string="Account payable (Prepayment)",
    #         view_load=True,
    #         domain="[('type', '=', 'payable')]",
    #         help="This account will be used instead of the default one as the \
    #         Prepayment payable account for the current partner",
    #         required=True),
    #     'property_account_prereceivable': fields.property(
    #         'account.account',
    #         type='many2one',
    #         relation='account.account',
    #         string="Account Receivable (Prepayment)",
    #         view_load=True,
    #         domain="[('type', '=', 'receivable')]",
    #         help="This account will be used instead of the default one as the \
    #         Prepayment receivable account for the current partner",
    #         required=True),
    # }


class account_voucher(osv.osv):
    _inherit = "account.voucher"

    _columns = {
        'purchase_id': fields.many2one(
            'purchase.order', 'Purchase Order',
            domain=[('invoiced', '=', False)],
            ondelete='set null'),
        'use_prepayment_account': fields.boolean(
            'Use Prepayment account',
            help="Check this if you want to input a prepayment \
            on the prepayment accounts."),
        'sale_id': fields.many2one(
            'sale.order', 'Sale Order', domain=[('invoiced', '=', False)],
            ondelete='set null'),
    }
    _defaults = {
        'use_prepayment_account': False,
    }

    def onchange_sale_id(self, cr, uid, ids, sale_id):
        res = {}
        if not sale_id:
            return res
        amount = 0
        so_obj = self.pool.get('sale.order')
        so = so_obj.browse(cr, uid, sale_id)
        if so.invoiced:
            res['warning'] = {'title': _('Warning!'),
                              'message': _('Selected Sale Order was paid.')}
        for invoice in so.invoice_ids:
            amount = invoice.residual
        res['value'] = {'partner_id': so.partner_id.id,
                        'amount': amount}
        return res

    def onchange_purchase_id(self, cr, uid, ids, purchase_id):
        res = {}
        if not purchase_id:
            return res
        amount = 0
        po_obj = self.pool.get('purchase.order')
        po = po_obj.browse(cr, uid, purchase_id)
        if po.invoiced:
            res['warning'] = {'title': _('Warning!'),
                              'message': _('Selected Purchase Order was \
                                paid.')}

        for invoice in po.invoice_ids:
            amount = invoice.residual
        res['value'] = {'partner_id': po.partner_id.id,
                        'amount':  amount}
        return res

    # def onchange_prepayment_account(self, cr, uid, ids,
    #                                 use_prepayment_account):
    #     res = {}
    #     if not use_prepayment_account:
    #         return res

    #     res['value'] = {'line_cr_ids': [], 'line_dr_ids': [], 'line_ids': []}
    #     return res
    def onchange_prepayment_account(self, cr, uid, ids,
                                    use_prepayment_account):
        res = {}
        line_cr_id = ""
        if not use_prepayment_account:
            line_cr_id = self.browse(cr, uid, fields)
            print "\n\n\nll%s\n\n\n" % line_cr_id
            return res

        res['value'] = {'line_cr_ids': [], 'line_dr_ids': [], 'line_ids': []}
        return res

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id,
                               name, company_currency, current_currency,
                               context=None):
        line_vals = super(account_voucher, self).writeoff_move_line_get(
            cr, uid, voucher_id, line_total, move_id, name, company_currency,
            current_currency, context=context)
        if line_vals:
            account_id = False
            voucher_brw = self.pool.get(
                'account.voucher').browse(cr, uid, voucher_id, context)
            if voucher_brw.use_prepayment_account:
                if voucher_brw.payment_option == 'with_writeoff':
                    account_id = voucher_brw.writeoff_acc_id.id
                elif voucher_brw.type in ('sale', 'receipt'):
                    if not voucher_brw.partner_id.\
                            property_account_prereceivable:
                        raise osv.except_osv(
                            _('Unable to validate payment !'),
                            _('Please configure the partner Prereceivable \
                                Account at first!'))
                    account_id = voucher_brw.partner_id.\
                        property_account_prereceivable.id
                else:
                    if not voucher_brw.partner_id.property_account_prepayable:
                        raise osv.except_osv(
                            _('Unable to validate payment !'),
                            _('Please configure the partner Prepayable Account\
                                at first!'))
                    account_id = voucher_brw.partner_id.\
                        property_account_prepayable.id
                if account_id:
                    line_vals['account_id'] = account_id
        return line_vals
account_voucher()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
