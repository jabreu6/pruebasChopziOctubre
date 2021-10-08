# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api

class WizardChopziOperations(models.TransientModel):
    _name = 'wizard.chopzi.config'
    _description = 'wizard'

    name = fields.Char(string="Nombre de la instancia")
    user = fields.Char(string="Usuario")
    chopzi_code = fields.Char(string="Codigo Chopzi")
    credencial = fields.Char(string="Credencial")
    dataBase = fields.Char(string="Base de Datos")

    def instanceChopzi(self):
        new_instance = {
            'name': self.name,
            'user': self.user,
            'chopzi_code': self.chopzi_code,
            'credencial': self.credencial,
            'dataBase': self.dataBase
        }
        instance_id = self.env['chopzi.config'].create(new_instance)
        self.env['chopzi.operations'].create({
            'instance': instance_id.id
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }