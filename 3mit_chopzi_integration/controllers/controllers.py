# -*- coding: utf-8 -*-
import json
import logging
import odoo
import pprint
import werkzeug
from werkzeug import urls
from datetime import datetime
from odoo import http
from odoo.http import request
from http import HTTPStatus
from ..constants import *

_logger = logging.getLogger(__name__)

class respartner_requets(http.Controller):
    @http.route('/createPartner', cors='*', type='http', methods=['POST'], auth='public', csrf=False)
    def func_requets(self, **post):
        response = []
        request_partner = json.loads(request.httprequest.data)
        cr, context, env = http.request.cr, http.request.context, http.request.env
        for data in request_partner:
            missing = self.validatorData(data)
            if missing == "":
                if data['is_creation'] == True:
                    state = env['res.country.state'].sudo().search([('name', 'like', 'acas'),('country_id','=',238)]).id
                    search = env['res.partner'].sudo().search([],limit=1, order="id desc")
                    if 'identification_id' in search:
                        if(data['is_company']==True):
                            if(len(data['identificator']) == 11 and (data['identificator'][0] == "J" or data['identificator'][0] == "V" or data['identificator'][0] == "G" or data['identificator'][0] == "E")):
                                search = env['res.partner'].sudo().search([('rif', '=', data['identificator'])]).id
                                if(search == False):
                                    try:
                                        createPartner = self.modelPartner(data,state)
                                        createPartner['people_type_company'] = 'pjdo'
                                        createPartner['rif'] = data['identificator']
                                        partner = env['res.partner'].sudo().create(createPartner)
                                        self.returnSuccess(data['identificator'],response) #CREADO
                                    except Exception as err:
                                        self.returnFailed(err, response, data['identificator']) #FALLO EN CREACION
                                else:
                                    self.returnRepeat(data['identificator'],response) #REPETIDO
                            else:
                                missing = "identificator  "
                                self.returnMissing(missing, response, data['identificator'])
                        elif(data['is_company']==False):
                            flag = False
                            if len(data['identificator']) >= 9 and len(data['identificator']) <= 10 and (data['identificator'][0] == 'V' or data['identificator'][0] == 'E'):
                                flag = True
                            elif len(data['identificator']) >= 12 and len(data['identificator']) <= 22 and data['identificator'][0] == 'P':
                                flag = True
                            if flag == True:
                                search = env['res.partner'].sudo().search([('identification_id', '=', data['identificator'][2:])]).id
                                if (search == False):
                                    try:
                                        createPartner = self.modelPartner(data,state)
                                        createPartner['nationality'] = data['identificator'][0]
                                        createPartner['identification_id'] = data['identificator'][2:]
                                        partner = env['res.partner'].sudo().create(createPartner)
                                        self.returnSuccess(data['identificator'], response)  # CREADO
                                    except Exception as err:
                                        self.returnFailed(err, response)  # FALLO EN CREACION
                                else:
                                    self.returnRepeat(data['identificator'], response)  # REPETIDO
                            else:
                                missing = "identificator  "
                                self.returnMissing(missing, response, data['identificator'])
                        else:
                            missing = "is_company  "
                            self.returnMissing(missing, response, data['name'])
                    else:
                        flag = False
                        if (data['is_company'] == True):
                            if(len(data['identificator']) == 11 and (data['identificator'][0] == "J" or data['identificator'][0] == "V" or data['identificator'][0] == "G" or data['identificator'][0] == "E")):
                                flag = True
                        elif (data['is_company'] == False):
                            if len(data['identificator']) >= 9 and len(data['identificator']) <= 10 and (data['identificator'][0] == 'V' or data['identificator'][0] == 'E'):
                                flag = True
                            elif len(data['identificator']) >= 12 and len(data['identificator']) <= 22 and data['identificator'][0] == 'P':
                                flag = True
                        if(flag == True):
                            search = env['res.partner'].sudo().search([('vat', '=', data['identificator'])]).id
                            if (search == False):
                                try:
                                    createPartner = self.modelPartner(data,state)
                                    createPartner['vat'] = data['identificator']
                                    partner = env['res.partner'].sudo().create(createPartner)
                                    self.returnSuccess(data['identificator'], response)  # CREADO
                                except Exception as err:
                                    self.returnFailed(err, response)  # FALLO EN CREACION
                            else:
                                self.returnRepeat(data['identificator'], response)  # REPETIDO
                        else:
                            missing = "identificator  "
                            self.returnMissing(missing, response, data['identificator'])
                else:
                    search = env['res.partner'].sudo().search([], limit=1, order="id desc")
                    if 'identification_id' in search:
                        if (data['is_company'] == True):
                            search = env['res.partner'].sudo().search([('rif', '=', data['identificator'])])
                            if (search != False):
                                try:
                                    partner = data
                                    partner['rif'] = data['identificator']
                                    writePartner = env['res.partner'].sudo().write(partner)
                                    self.returnEdit(partner['rif'], response)  # CREADO
                                except Exception as err:
                                    self.returnFailed(err, response, data['identificator'])  # FALLO EN CREACION
                            else:
                                self.returnNotFound(data['identificator'], response)  # NO EXISTE
                        elif (data['is_company'] == False):
                            search = env['res.partner'].sudo().search([('identification_id', '=', data['identificator'][2:])])
                            if (search != False):
                                try:
                                    partner = data
                                    partner['identification_id'] = data['identificator'][2:]
                                    partner['nationality'] = data['identificator'][0]
                                    writePartner = env['res.partner'].sudo().write(partner)
                                    info = partner['nationality'] + "-" + partner['identification_id']
                                    self.returnEdit(info, response)  # CREADO
                                except Exception as err:
                                    self.returnFailed(err, response)  # FALLO EN CREACION
                            else:
                                self.returnNotFound(data['identificator'], response)  # NO EXISTE
                        else:
                            missing = "identificator  "
                            self.returnMissing(missing, response, data['name'])
                    else:
                        search = env['res.partner'].sudo().search([('vat', '=', data['identificator'])])
                        if (search != False):
                            try:
                                partner = data
                                partner['vat'] = data['identificator']
                                writePartner = env['res.partner'].sudo().write(partner)
                                self.returnEdit(partner['vat'], response)  # CREADO
                            except Exception as err:
                                self.returnFailed(err, response)  # FALLO EN CREACION
                        else:
                            self.returnNotFound(data['identificator'], response)  # NO EXISTE
            else:
                self.returnMissing(missing, response)
        res = {
            'status_code': HTTPStatus.OK,
            'data': response
        }
        return json.dumps(res)


    def validatorData(self, data):
        missing = ""
        if "name" not in data:
            missing = missing + "name, "
        if "identificator" not in data:
            missing = missing + "identificator, "
        if "birth_date" not in data:
            missing = missing + "birth_date, "
        if "gender" not in data:
            missing = missing + "gender, "
        if "is_company" not in data:
            missing = missing + "is_company, "
        if "phone" not in data:
            data['phone'] = False
        if "email" not in data:
            data['email'] = False
        if "address" not in data:
            data['address'] = False
        return missing

    def returnRepeat(self, partner, response):
        status_partner = {
            'status_code': HTTPStatus.NOT_ACCEPTABLE,
            'content': STATUS['406Repeat'],
            'contact': partner
        }
        response.append(status_partner)

    def returnFailed(self, err, response, partner):
        status_partner = {
            'status_code': HTTPStatus.CONFLICT,
            'content': err,
            'contact': partner
        }
        response.append(status_partner)

    def returnSuccess(self, partner, response):
        status_partner = {
            'status_code': HTTPStatus.CREATED,
            'content': STATUS['201'],
            'contact': partner
        }
        response.append(status_partner)

    def returnMissing(self, missing, response, partner):
        missing = missing[:len(missing) - 2]
        status_partner = {
            'status_code': HTTPStatus.UNPROCESSABLE_ENTITY,
            'content': STATUS['422'] + missing,
            'contact': partner
            }
        response.append(status_partner)

    def returnEdit(self, partner, response):
        status_partner = {
            'status_code': HTTPStatus.OK,
            'content': STATUS['200'],
            'contact': partner
        }
        response.append(status_partner)

    def returnNotFound(self, partner, response):
        status_partner = {
            'status_code': HTTPStatus.NOT_FOUND,
            'content': STATUS['404'],
            'contact': partner
        }
        response.append(status_partner)

    def modelPartner(self, partner, state):
        contact = {
            'is_company': partner['is_company'],
            "name": partner['name'],
            "phone": partner['phone'],
            "email": partner['email'],
            'street': partner['address'],
            'birth_date': partner['birth_date'],
            'gender': partner['gender'],
            'street2': 'NA',
            'zip': '0000',
            'city': 'NA',
            'country_id': 238,
            'state_id' : state
        }
        return contact

