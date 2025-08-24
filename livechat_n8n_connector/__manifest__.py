# -*- coding: utf-8 -*-
{
    'name': "Livechat N8N Connector",
    'summary': """
        Connect Odoo's Livechat with an N8N webhook for automated responses.
    """,
    'description': """
        This module intercepts messages from livechat channels and sends them to a configurable N8N webhook.
        It then waits for a reply from the webhook and posts it back to the chat, acting as a bot.

        Features:
        - Intercepts new livechat messages.
        - Triggers a webhook only for visitor messages (not from admin).
        - Sends message content and channel UUID to the webhook.
        - Posts the response from the webhook back to the chat.
        - Adds a configuration field in General Settings to set the N8N webhook URL.
    """,
    'author': "Jules",
    'website': "https://github.com/jules-agent",
    'category': 'Website/Livechat',
    'version': '18.0.1.0.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'im_livechat', 'website_livechat'],

    # always loaded
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}