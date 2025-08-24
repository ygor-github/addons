# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    n8n_livechat_webhook_url = fields.Char(
        string="URL del Webhook de n8n para Livechat",
        config_parameter='livechat_n8n_connector.webhook_url',
        help="Introduce la URL del webhook de n8n que recibirá los mensajes del livechat."
    )