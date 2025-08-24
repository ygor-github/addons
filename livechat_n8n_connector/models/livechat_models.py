# -*- coding: utf-8 -*-

import json
import logging
import requests
import threading
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# === All model definitions in one file to aid loading order ===


class ResCompany(models.Model):
    """Adds the webhook URL to the company model."""
    _inherit = 'res.company'

    n8n_webhook_url = fields.Char(
        string='N8N Webhook URL',
        help="The URL of the N8N webhook to send livechat messages to."
    )


class ResConfigSettings(models.TransientModel):
    """Adds the related field to the settings view."""
    _inherit = 'res.config.settings'

    n8n_webhook_url = fields.Char(
        related='company_id.n8n_webhook_url',
        string='N8N Webhook URL',
        readonly=False,
        help="The URL of the N8N webhook to send livechat messages to."
    )


class MailMessage(models.Model):
    """Intercepts livechat messages and triggers the webhook."""
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        """
        Intercepts the creation of a new message. If it's from a livechat
        and not from the admin, it triggers a webhook.
        """
        message = super(MailMessage, self).create(vals)

        # Use a separate thread to avoid blocking the main UI thread
        if message.author_id and message.model == 'im_livechat.channel' and message.body:
            author_name = message.author_id.name
            if 'Admin' not in author_name and 'OdooBot' not in author_name:
                thread = threading.Thread(target=self._trigger_n8n_webhook, args=(message,))
                thread.daemon = True
                thread.start()

        return message

    def _get_n8n_webhook_url(self):
        """Safely retrieve the webhook URL from the current company's settings."""
        # Use a new cursor for the threaded environment
        with self.pool.cursor() as cr:
            env = api.Environment(cr, self.env.uid, self.env.context)
            return env.company.n8n_webhook_url

    def _trigger_n8n_webhook(self, message):
        """
        Sends the message to the N8N webhook and processes the response.
        This method is designed to be run in a separate thread.
        """
        webhook_url = self._get_n8n_webhook_url()
        if not webhook_url:
            _logger.warning("N8N webhook URL is not set. Skipping webhook trigger.")
            return

        # We need a new environment and cursor for the thread
        with self.pool.cursor() as cr:
            env = api.Environment(cr, self.env.uid, self.env.context)
            livechat_channel = env['im_livechat.channel'].search([
                ('id', '=', message.res_id)
            ], limit=1)

            if not livechat_channel:
                return

            payload = {
                'message': message.body,
                'channel_uuid': livechat_channel.uuid,
            }

            try:
                _logger.info(f"Sending to N8N webhook: {payload}")
                response = requests.post(
                    webhook_url,
                    data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()

                response_data = response.json()
                if response_data.get('reply'):
                    # Pass the env to the reply method
                    self.with_env(env)._post_bot_reply(livechat_channel, response_data['reply'])

            except requests.exceptions.Timeout:
                _logger.error("Request to N8N webhook timed out.")
            except requests.exceptions.RequestException as e:
                _logger.error(f"Error calling N8N webhook: {e}")
            except json.JSONDecodeError:
                _logger.error(f"Could not decode JSON response from N8N webhook. Response: {response.text}")

    def _post_bot_reply(self, channel, reply_text):
        """
        Posts a message to the livechat channel as the Administrator (OdooBot).
        """
        # The environment should already be thread-safe from the caller
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        if not admin_user:
            _logger.error("Could not find Administrator user (base.user_admin).")
            return

        author_id = admin_user.partner_id.id

        channel.message_post(
            body=reply_text,
            author_id=author_id,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        _logger.info(f"Posted bot reply to channel {channel.uuid}: {reply_text}")
