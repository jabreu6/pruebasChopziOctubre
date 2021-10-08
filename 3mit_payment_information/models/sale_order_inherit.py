# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    payment_data = fields.Text(string='Payment data')
    bool_payment_data = fields.Boolean(string="¿Hay payment data?")

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrderInherit, self)._create_invoices()
        if self.payment_data != "":
            self.bool_payment_data = True
        else:
            self.bool_payment_data = False
        return res
