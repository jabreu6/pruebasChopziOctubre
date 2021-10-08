# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    _sql_constraints = [
        ('code_name_unique', 'unique(ref_tipo_pago,code)',
         "Ya existe un tipo de pago con esta referencia y nombre. Por favor, edite el existente o añada uno nuevo.")
    ]

    ref_tipo_pago = fields.Char(string="Referencia/tipo de pago", size=2,
                                help="Código de transferencias ingresado por el usuario")
