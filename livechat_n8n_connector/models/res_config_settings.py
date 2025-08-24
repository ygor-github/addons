# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    n8n_webhook_url = fields.Char(
        string='N8N Webhook URL',
        config_parameter='livechat_n8n_connector.n8n_webhook_url',
        help="The URL of the N8N webhook to send livechat messages to."
    )