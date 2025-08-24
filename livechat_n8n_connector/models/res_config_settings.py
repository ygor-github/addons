# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    n8n_webhook_url = fields.Char(
        string='N8N Webhook URL',
        config_parameter='livechat_n8n_connector.n8n_webhook_url',
        help="The URL of the N8N webhook to send livechat messages to."
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'livechat_n8n_connector.n8n_webhook_url',
            self.n8n_webhook_url or ''
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            n8n_webhook_url=self.env['ir.config_parameter'].sudo().get_param(
                'livechat_n8n_connector.n8n_webhook_url', ''
            ),
        )
        return res