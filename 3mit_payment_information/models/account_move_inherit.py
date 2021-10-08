# -*- coding: utf-8 -*-
import datetime

from odoo import models
from odoo.exceptions import Warning

import ast


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_register_payment(self):
        res = super(AccountMoveInherit, self).action_register_payment()
        if self.invoice_origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
            if sale_order.bool_payment_data:
                payment_information = sale_order.payment_data
                payment_information = ast.literal_eval(payment_information)
                payment_information_aux = []
                aux = ""
                for info in payment_information:
                    account_journal = self.env['account.journal'].search([('ref_tipo_pago', '=', info.get('code'))])
                    account_payment_register = self.env['account.payment.register'].with_context(active_ids=self.ids, active_model='account.move', active_id=self.id)
                    if not account_journal:
                        payment_information_aux.append(info)
                        aux += str(info.get('code')) + ', '
                    else:
                        if self.amount_residual != 0:
                            payment_difference_handling = 'open'
                        else:
                            payment_difference_handling = 'reconcile'

                        if not self.partner_id.bank_ids:
                            partner_bank_id = False
                        else:
                            partner_bank_id = self.partner_id.bank_ids[0]._origin
                            partner_bank_id = partner_bank_id.id

                        new_account_payment_register = account_payment_register.create({
                            'payment_date': datetime.datetime.today(),
                            'amount': float(info['amount']),
                            'communication': self.name,
                            'group_payment': True,
                            'currency_id': self.company_id.currency_id.id,
                            'journal_id': account_journal.id,
                            'partner_bank_id': partner_bank_id,
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'source_amount': self.amount_residual,
                            'source_amount_currency': float(info['amount']),
                            'payment_method_id': account_journal.inbound_payment_method_ids.ids[0],
                            'company_id': self.env.company.id,
                            'partner_id': self.partner_id.id,
                            'payment_difference_handling': payment_difference_handling,
                        })
                        account_payment = self.env['account.payment'].create({
                            'date': new_account_payment_register.payment_date,
                            'amount': new_account_payment_register.amount,
                            'payment_type': new_account_payment_register.payment_type,
                            'partner_type': new_account_payment_register.partner_type,
                            'ref': new_account_payment_register.communication,
                            'journal_id': new_account_payment_register.journal_id.id,
                            'currency_id': new_account_payment_register.currency_id.id,
                            'partner_id': new_account_payment_register.partner_id.id,
                            'partner_bank_id': new_account_payment_register.partner_bank_id.id,
                            'payment_method_id': new_account_payment_register.payment_method_id.id,
                            'destination_account_id': self.bank_partner_id.property_account_receivable_id.id,
                        })
                        account_payment.action_post()

                        to_reconcile = None
                        if new_account_payment_register.group_payment:
                            to_reconcile = new_account_payment_register.line_ids

                        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
                        if account_payment.state != 'posted':
                            continue

                        payment_lines = account_payment.line_ids.filtered_domain(domain)
                        for account in payment_lines.account_id:
                            (payment_lines + to_reconcile).filtered_domain([('account_id', '=', account.id),
                                                                            ('reconciled', '=', False)]).reconcile()
                if aux != "":
                    aux = aux[:len(aux)-2]
                    sale_order.payment_data = str(payment_information_aux)
                    return aux
                else:
                    sale_order.payment_data = ""
                    sale_order.bool_payment_data = False
                    return aux
            else:
                if self.amount_residual and self.invoice_outstanding_credits_debits_widget != 'false':
                    raise Warning("No se ha encontrado información del pago o se ha procesado toda la información.\n"
                                  "Se han encontrado créditos pendientes, usted puede añadir uno si lo desea.")
                elif self.amount_residual and self.invoice_outstanding_credits_debits_widget == 'false':
                    return res
        else:
            return res

    def action_register_payment_button(self):
        return_value = self.action_register_payment()
        if isinstance(return_value, str):
            if return_value != "":
                return_name = "¡Advertencia!"
                wizard_msg = self.env['message.wizard']\
                    .create({'message': ("No existe un diario asociado al código: %s.\n Por favor, cree uno o contacte"
                                         " con el administrador." % return_value)})
            else:
                return_name = "¡Éxito!"
                wizard_msg = self.env['message.wizard'].create({'message': "Se han procesado los pagos exitosamente."})
            return {
                'name': return_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                'res_id': wizard_msg.id,
                'target': 'new'
            }
        elif isinstance(return_value, dict):
            return return_value
