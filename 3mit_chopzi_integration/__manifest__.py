# -*- coding: utf-8 -*-
{
    'name': "Chopzi integration",

    'summary': """
        Integración 3MIT para Chopzi para gestión de inventario, productos y usuarios.""",

    'description': """
        Colaborador: Freddy Castillo
    """,

    'author': "3MIT",
    'website': "https://www.3mit.dev",
    'category': 'Productivity/VOIP',
    'version': '1.1',

    'depends': ['base', 'contacts', 'stock', 'product','purchase', 'web_notify'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_chopzi_config.xml',
        'wizard/wizard_chopzi_operations.xml',
        'views/chopzi_operations.xml',
        'views/chopzi_config.xml',
        'views/menuitem_root_view.xml',
        'views/inherit/res_partner.xml',
    ],

    'application': True,
    'instalable': True,
    'post_init_hook': 'creacion_estado',
}
