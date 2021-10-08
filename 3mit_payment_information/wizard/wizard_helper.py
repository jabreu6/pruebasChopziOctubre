# -*- coding: utf-8 -*-
from odoo import models, fields


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    _description = 'Helper wizard message'

    message = fields.Text('Message')

    def action_ok(self):
        for _ in self:
            return {'type': 'ir.actions.act_window_close'}
