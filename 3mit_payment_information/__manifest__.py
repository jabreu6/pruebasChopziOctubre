# -*- coding: utf-8 -*-
{
    'name': "Registro de pago automático",

    'summary': """
        Registra el pago automáticamente hecho desde la api en las Facturas.""",

    'description': """
        * Automatiza el registro del pago en las facturas.
        * Añade código de transferencia único (uso externo) en los Diarios.
        * Añade validación en el diario para el código de transferencia único.
        * Añade campo auxiliar para la identificación/rif en el módulo de contactos.
        \nElaborado por: Kleiver Pérez.
    """,

    'author': "3MIT",
    'website': "https://www.3mit.dev",
    'category': 'Accounting',
    'version': '1.2.2',

    'depends': ['base', 'account_accountant', 'sale_management', 'contacts', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal_inherit_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/account_move_inherit_view.xml',
        'wizard/wizard_helper.xml'
    ],
    'demo': [
    ],
}
