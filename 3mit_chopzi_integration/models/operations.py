from odoo import models, fields, api

class ChopziOperations(models.Model):
    _name = 'chopzi.operations'
    _description = 'operacion'

    name = fields.Char(string="nombre")
    instance = fields.Many2one('chopzi.config', string='Instancia')

    instance_name = fields.Char(related='instance.name', string='Nombre de instancia')
    instance_user = fields.Char(related='instance.user', string='Usuario')
    instance_dataBase = fields.Char(related='instance.dataBase', string='Base de Datos')
    instance_chopzi_code = fields.Char(related='instance.chopzi_code', string='Codigo Chopzi')

    def call_wizard(self):
        return {
            'name': 'Operaciones',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.chopzi.operations',
            'target': 'new',
            'context': {'default_instance_id': self.instance.id}
        }

