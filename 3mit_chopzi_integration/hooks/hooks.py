from odoo import api, SUPERUSER_ID

def creacion_estado(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # creacion de estado
    state = env['res.country.state'].sudo().search([('name', '=', 'Caracas')]).id
    if state == False:
        env['res.country.state'].sudo().create({'country_id':238, 'name':'Caracas', 'code':'1071'})