# -*- coding: utf-8 -*-
import datetime
from requests import post
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError, except_orm
from ..constants import *
import dateutil.parser
import json

# TODO: CASE SQL - FORMAT SQL PARA LA BETA
# REESTRUCTURAR EL SEARCH PARA EVITAR EL FOR, UN PARAMETRO LLAMADO FIELDS
# LIMITAR LA INSTANCIA A 1???
# HACER UNA API, METODO CREAR CONTACTOS Y ESO SE ENVIA
# VALIDAR ENTRADA, IGUAL QUE SIEMRPE, POR LOS MOMENTOS HACE UN IF 214 VALIDATE SUBCRIPCION
#Masivo no crea sino envia


class WizardChopziOperations(models.TransientModel):
    _name = 'wizard.chopzi.operations'
    _description = 'wizard'

    fecha_hoy = datetime.datetime.now()

    instance_id = fields.Many2one("chopzi.config", string="Instancias", readonly=True)

    opcions = fields.Selection(selection= [
        ('sync_contact', 'Contactos'),
        ('sync_product', 'Productos'),
        ('sync_stock', 'Inventario'),
    ], string="Opciones")

    date_from = fields.Date(default=fecha_hoy, string="Desde")
    date_to = fields.Date(default=fecha_hoy, string="Hasta")
    atribute_all = fields.Boolean(default=False, string="Todos")

    def selected(self):
        self.revisionDate()
        data = []
        if(self.atribute_all == True): #SINCRONIZA TODA LAS FECHAS
            if(self.opcions == 'sync_contact'): #SINCRONIZA CONTACTOS
                search = self.env['res.partner'].search([], order='id asc')
                self.sendPartner(search,data)

            elif(self.opcions == 'sync_product'): #SINCRONIZA PRODUCTOS
                search = self.env['product.template'].search([], order="id asc")
                a = self.sendProduct(search, data)


            elif(self.opcions == 'sync_stock'): #SINCRONIZA STOCK
                search = self.env['product.template'].search([], order="id asc")
                self.sendStock(search, data)

        else: #SINCRONIZA ALGUNAS FECHAS
            if (self.opcions == 'sync_contact'): # SINCRONIZA CONTACTOS
                search = self.env['res.partner'].search([("create_date", ">=", self.date_from), ("create_date", "<=", self.date_to)], order='id asc')
                self.sendPartner(search,data)

            elif (self.opcions == 'sync_product'): # SINCRONIZA PRODUCTOS
                search = self.env['product.template'].search([("create_date",">=",self.date_from),("create_date","<=",self.date_to)], order="id asc")
                self.sendProduct(search, data)

            elif (self.opcions == 'sync_stock'): # SINCRONIZA STOCK
                search = self.env['product.template'].search([("create_date", ">=", self.date_from), ("create_date", "<=", self.date_to)], order="id asc")
                self.sendStock(search, data)

    def sendProduct(self, products, data):
        if len(products) > 0:
            for product in products:
                information = {
                    "odoo_id": product.id,
                    "name": product.name,
                    "sale_price": product.list_price,
                    "inventory": product.qty_available
                }
                data.append(information)
            information = {
                "client_code": self.instance_id.chopzi_code,
                "data": data
            }
            try:
                snap = post(URL['product'], json=information)
                message = json.loads(snap.text)
                self.env.user.notify_info(title="Notificación", message=message['odoo'])
            except:
                raise AccessError('No pudo enviar la información, por favor intente más tarde')
        else:
            raise UserError('No existe información para las fechas seleccionadas')

    def sendStock(self, products, data):
        if len(products) > 0:
            for product in products:
                information = {
                    "odoo_id": product.id,
                    "name": product.name,
                    "quantity": product.qty_available
                }
                data.append(information)
            information = {
                "client_code": self.instance_id.chopzi_code,
                "data": data
            }
            try:
                snap = post(URL['stock'], json=information)
                message = json.loads(snap.text)
                self.env.user.notify_info(title="Notificación", message=message['odoo'])
            except:
                raise AccessError('No pudo enviar la información, por favor intente más tarde')
        else:
            raise UserError('No existe información para las fechas seleccionadas')

    def sendPartner(self, element, data):
        if len(element) > 0:
            search = self.env['res.partner'].search([], limit=1)
            if "identification_id" in search:
                for partner in element:
                    if (partner.is_company == True):
                        contact = {
                            "name": partner.name,
                            "phone": str(partner.phone),
                            "email": partner.email,
                            "identificator": partner.rif,
                            "birth_date": "",
                            "gender": "",
                        }
                    else:
                        contact = {
                            "name": partner.name,
                            "phone": str(partner.phone),
                            "email": partner.email,
                            "identificator": partner.identification_id,
                            "birth_date": partner.birth_date,
                            "gender": partner.gender,
                        }
                    data.append(contact)
                information = {
                    "client_code": self.instance_id.chopzi_code,
                    "data": data
                }
            else:
                for partner in element:
                    contact = {
                        "name": partner.name,
                        "phone": str(partner.phone),
                        "email": partner.email,
                        "identificator": partner.vat,
                        "birth_date": partner.birth_date,
                        "gender": partner.gender,
                    }
                    data.append(contact)
                information = {
                    "client_code": self.instance_id.chopzi_code,
                    "data": data
                }
            try:
                snap = post(URL['partner'], json=information)
                message = json.loads(snap.text)
                self.env.user.notify_info(title="Notificación", message=message['odoo'])
            except:
                raise AccessError('No pudo enviar la información, por favor intente más tarde')
        else:
            raise UserError('No existe información para las fechas seleccionadas')

    def revisionDate(self):
        hoy = dateutil.parser.parse(str(self.fecha_hoy)).date()
        if self.date_from > self.date_to:
            raise ValidationError('La fecha ingresada en el recuadro izquierdo no puede ser mayor al derecho')
        if self.date_from > hoy:
            raise ValidationError('La fecha ingresada en el recuadro izquierdo no puede ser mayor a {}'.format(hoy))
        if self.date_to > hoy:
            raise ValidationError('La fecha ingresada en el recuadro a la derecha no puede ser mayor a {}'.format(hoy))

