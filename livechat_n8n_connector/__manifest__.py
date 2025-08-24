# -*- coding: utf-8 -*-
{
    'name': "Conector de Livechat con n8n",
    'version': '1.0',
    'summary': "Integra el Livechat de Odoo con n8n mediante webhooks.",
    # ... (descripción, etc.)
    'author': "Tu Nombre",
    'category': 'Website/Livechat',
    'depends': [
        'im_livechat',
        'website_livechat', # <-- La dependencia clave
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}