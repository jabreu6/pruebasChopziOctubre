from odoo import models, fields, api
from requests import post
from ...constants import *
import json
from odoo.exceptions import AccessError

class ChopziStockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model_create_multi
    def create(self, vals_list):
        if 'inventory_quantity' in vals_list[0]:
            chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
            if(chopzi_code != False):
                stock = {
                    "client_code": chopzi_code,
                    "odoo_id": vals_list[0]['product_id'],  # PRODUCT ID,
                    "quantity": vals_list[0]['inventory_quantity'],
                    "location_id": vals_list[0]['location_id'],
                }
                try:
                    snap = post(URL['stockCRUD'], json=stock)
                    message = json.loads(snap.text)
                    self.env.user.notify_info(title="Notificación", message=message['odoo'])
                except:
                    self.env.user.notify_warning(message='No pudo enviar la información, por favor intente más tarde')
        res = super(ChopziStockQuant, self).create(vals_list)
        return res

    def write(self, values):
        if len(values) == 1:
            if "inventory_quantity" in values and id in self:
                chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
                if (chopzi_code != False):
                    stock = {
                        "client_code": chopzi_code,
                        "odoo_id": self.product_id,  # PRODUCT ID,
                        "quantity": values['inventory_quantity'],
                        "location_id": self.location_id
                    }
                    try:
                        snap = post(URL['stockCRUD'], json=stock)
                        message = json.loads(snap.text)
                        self.env.user.notify_info(title="Notificación", message=message['odoo'])
                    except:
                        self.env.user.notify_warning(
                            message='No pudo enviar la información, por favor intente más tarde')
        super(ChopziStockQuant, self).write(values)


class ChopziStockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(ChopziStockPicking, self).button_validate()
        if(res == True):
            chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
            if (chopzi_code != False):
                for product in self.move_line_ids:
                    quantity = product.product_id.free_qty
                    odoo_id = product.product_id.id
                    location_id = product.location_id.id
                    stock = {
                        "client_code": chopzi_code,
                        "odoo_id": odoo_id,  # PRODUCT ID,
                        "quantity": quantity,
                        "location_id": location_id,
                    }
                    try:
                        snap = post(URL['stockCRUD'], json=stock)
                        message = json.loads(snap.text)
                        self.env.user.notify_info(title="Notificación", message=message['odoo'])
                    except:
                        self.env.user.notify_warning(message='No pudo enviar la información, por favor intente más tarde')
        return res
