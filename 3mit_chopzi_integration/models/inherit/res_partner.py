import datetime
import re

from odoo import models, fields, api
from requests import post
from ...constants import *
import json
from odoo.exceptions import AccessError

class ChopziResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection(selection=[("M","Hombre"),("F","Mujer")], string="Genero")
    birth_date = fields.Date(string="Nacimiento")

    @api.model_create_multi
    def create(self, vals_list):
        #TODO: REVISAR LOCALIZACION VALIDATION TELEFONO, cambiar position 0 por FOR por sia caso se hace importacion
        res = super(ChopziResPartner, self).create(vals_list)
        chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
        if(chopzi_code != False):
            for partner in vals_list:
                if partner['phone'] == False:
                     partner['phone'] = ""
                if partner['email'] == False :
                    partner['email'] = ""
                search = self.env['res.partner'].search([], limit=1)
                if 'identification_id' in search:
                    if partner['is_company'] == False:
                        if "nationality" not in partner:
                            partner['nationality'] = partner['identification_id']
                            partner['identification_id'] = partner['identification_id'].lstrip("-")
                        contact = self.modelPartner(chopzi_code,partner)
                        contact['identificator'] = partner['nationality'] + '-' + partner['identification_id']
                        contact['gender'] = partner['gender']
                        contact['birth_date'] = partner['birth_date']
                    else:
                        contact = self.modelPartner(chopzi_code, partner)
                        contact['identificator'] = partner['rif']
                else:
                    if (partner['is_company'] == True):
                        contact = self.modelPartner(chopzi_code, partner)
                        contact['identificator'] = partner['vat']
                    else:
                        contact = self.modelPartner(chopzi_code, partner)
                        contact['identificator'] = partner['vat']
                        contact['gender'] = partner['gender']
                        contact['birth_date'] = partner['birth_date']
                try:
                    snap = post(URL['partnerCRUD'], json=contact)
                    message = json.loads(snap.text)
                    self.env.user.notify_info(title="Notificación", message=message['odoo'])
                except:
                    self.env.user.notify_warning(message='No pudo enviar la información, por favor intente más tarde')
        return res

    def write(self, values):
        res = super(ChopziResPartner, self).write(values)
        if (len(values) == 0):
            pass
        if(len(values)==1):
            pass
        elif ('reminder_date_before_receipt' in values or 'receipt_reminder_email' in values):
            pass
        elif('property_stock_customer' in values or 'property_stock_supplier' in values):
            pass
        elif(len(values) == 10):
            if 'vat' == False:
                pass
        else:
            chopzi_code = self.env['chopzi.operations'].search([], limit=1).instance_chopzi_code
            if (chopzi_code != False):
                flag = False  # aux de Missing
                missing = 0
                values = self.validatorWrite(values)
                if self.id != False:
                    search = self.env['res.partner'].search([('name','=',self.name), ('create_date','=',self.create_date)])
                    missing = self.revisionPartner(values, search)
                else:
                    if "identificator" in values:
                        if "identification_id" in values:
                            search = self.env['res.partner'].search([('identification_id','=',values['identification_id'])])
                            if "identificator" in values:
                                values.pop('identificator')
                            partner = self.env['res.partner'].browse(search.id)
                            self.modelAPI(partner, values)
                        if "rif" in values:
                            search = self.env['res.partner'].search([('rif', '=', values['rif'])])
                            if "identificator" in values:
                                values.pop('identificator')
                            partner = self.env['res.partner'].browse(search.id)
                            self.modelAPI(partner, values)
                        if "vat" in values:
                            search = self.env['res.partner'].search([('vat', '=', values['vat'])])
                            if "identificator" in values:
                                values.pop('identificator')
                            partner = self.env['res.partner'].browse(search.id)
                            self.modelAPI(partner, values)
                if "identification_id" in search:
                    if search.identification_id != False:
                        if "identification_id" not in values:
                            values['identification_id'] = self.identification_id
                            missing = missing + 1
                        if "nationality" not in values:
                            values['nationality'] = self.nationality
                            missing = missing + 1
                        if missing < 7:
                            flag = True
                            contact = self.modelPartnerWrite(chopzi_code,values)
                            contact['identificator'] = values['nationality'] + "-" + values['identification_id']
                    else:
                        if "rif" not in values:
                            values['rif'] = self.rif
                            missing = missing + 1
                        if missing < 6:
                            flag = True
                            contact = self.modelPartnerWrite(chopzi_code, values)
                            contact['identificator'] = values['rif']
                else:
                    if "vat" not in values:
                        values['vat'] = self.vat
                        missing = missing + 1
                    if missing < 6:
                        flag = True
                        contact = self.modelPartnerWrite(chopzi_code,values)
                        contact['identificator'] = values['vat']
                if flag == True:
                    try:
                        snap = post(URL['partnerCRUD'], json=contact)
                        message = json.loads(snap.text)
                        self.env.user.notify_info(title="Notificación", message=message['odoo'])
                    except:
                        self.env.user.notify_warning(message='No pudo enviar la información, por favor intente más tarde')
            return res

    def validatorWrite(self,values):
        if "phone" not in values and self.phone == False:
            values["phone"] = ""
        elif "phone" not in values and self.phone:
            values["phone"] = self.phone
        if "email" not in values and self.email == False:
            values["email"] = ""
        elif "email" not in values and self.email:
            values["email"] = self.email
        if "name" not in values:
            values['name'] = self.display_name
        if "birth_date" not in values:
            values['birth_date'] = self.birth_date
        if values['birth_date'] == False:
            values['birth_date'] == ""
        if "gender" not in values:
            values['gender'] = self.gender
        if values['gender'] == False:
            values['gender'] == ""
        return values

    def revisionPartner(self, partnerEdit, partner):
        missing = 0
        if partnerEdit['phone'] == partner.phone or partnerEdit['phone'] == "":
            missing = missing + 1
        if partnerEdit['email'] == partner.email or partnerEdit['email'] == "":
            missing = missing + 1
        if partnerEdit['name'] == partner.name:
            missing = missing + 1
        if partnerEdit['birth_date'] == partner.birth_date:
            missing = missing + 1
        if partnerEdit['gender'] == partner.gender:
            missing = missing + 1
        return missing

    def modelPartner(self, chopzi_code, partner):
        contact = {
            "is_creation": True,
            "client_code": chopzi_code,
            "name": partner['name'],
            "phone": str(partner['phone']),
            "email": partner['email']
        }
        return contact

    def modelPartnerWrite(self, chopzi_code, values):
        contact = {
            "is_creation": False,
            "client_code": chopzi_code,
            "name": values['name'],
            "phone": str(values['phone']),
            "email": values['email'],
            "gender": values['gender'],
            "birth_date": str(values['birth_date'])
        }
        return contact

    def modelAPI(self, partner, values):
        partner.name = values['name']
        partner.phone = values['phone']
        partner.email = values['email']
        partner.gender = values['gender']
        partner.birth_date = values['birth_date']
        partner.is_company = values['is_company']