from odoo import models, fields, api


class ChopziConfig(models.Model):
    _name = 'chopzi.config'
    _description = 'configuracion'

    name = fields.Char(string='Nombre de instancia')
    chopzi_code = fields.Char(string='Codigo')
    user = fields.Char(string='Usuario')
    credencial = fields.Char(string='Credenciales')
    dataBase = fields.Char(string='Base de Datos')

    def unlink(self):
        res = super(ChopziConfig, self).unlink()
        query = """DELETE FROM chopzi_operations WHERE id = {}""".format(self.id)
        self._cr.execute(query)
        self._cr.commit()
        return {
            'type': res,
            'tag': 'reload',
        }
