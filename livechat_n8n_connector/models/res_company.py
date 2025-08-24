# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    n8n_webhook_url = fields.Char(
        string='N8N Webhook URL',
        help="The URL of the N8N webhook to send livechat messages to."
    )
