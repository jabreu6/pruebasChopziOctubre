from odoo import models, fields, api
from requests import post
from ...constants import *
import json
from odoo.exceptions import AccessError

class ChopziProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.model_create_multi
    def create(self, vals_list):
        res = super(ChopziProductTemplate, self).create(vals_list)
        chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
        if chopzi_code != False:
            for product in vals_list:
                if "qty_available" not in product:
                    product['qty_available'] = 0
                product_id = self.env['product.template'].search([], limit=1, order='id desc').id
                product = {
                    "is_creation": True,
                    "client_code": chopzi_code,
                    "odoo_id": product_id,
                    "name": product['name'],
                    "sale_price": product['list_price'],
                    "inventory": product['qty_available']
                }
                try:
                    snap = post(URL['productCRUD'], json=product)
                    message = json.loads(snap.text)
                    self.env.user.notify_info(title="Notificación",message=message['odoo'])
                except:
                    self.env.user.notify_warning(message='No pudo enviar la información, por favor intente más tarde')
        return res

    def write(self, values):
        res = super(ChopziProductTemplate, self).write(values)
        if 'seller_ids' in values:
            pass
        else:
            chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
            if chopzi_code != False:
                missing = self.revisionWrite(values)
                if missing < 3:
                    product = {
                        "is_creation": False,
                        "client_code": chopzi_code,
                        "odoo_id": self.id, #PRODUCT ID,
                        "name": values['name'],
                        "sale_price": values['list_price'],
                        "inventory": values['qty_available'],
                    }
                    try:
                        snap = post(URL['productCRUD'], json=product)
                        message = json.loads(snap.text)
                        self.env.user.notify_info(title="Notificación",message=message['odoo'])
                    except:
                        self.env.user.notify_warning(title="Error", message='No pudo enviar la información, por favor intente más tarde')
            return res

    def revisionWrite(self, values):
        missing = 0
        if "name" not in values:
            values['name'] = self.name
            missing = missing + 1
        if "list_price" not in values:
            values['list_price'] = self.list_price
            missing = missing + 1
        if "qty_available" not in values:
            values['qty_available'] = self.qty_available
            missing = missing + 1
        return missing