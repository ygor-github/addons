# -*- coding: utf-8 -*-
import requests
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(MailMessage, self).create(vals_list)
        
        # Obtenemos la URL del webhook desde los parámetros del sistema
        config_parameter = self.env['ir.config_parameter'].sudo()
        n8n_url = config_parameter.get_param('livechat_n8n_connector.webhook_url')

        # Si no hay URL configurada, no hacemos nada
        if not n8n_url:
            return records

        # Partner del Administrador (OdooBot) para no responder a nuestros propios mensajes
        admin_partner = self.env.ref('base.partner_root')

        for rec in records:
            # Condiciones para activar el webhook:
            # 1. Es un mensaje de un canal (mail.channel)
            # 2. El canal es de tipo livechat
            # 3. El autor NO es el administrador (para evitar bucles)
            # 4. El mensaje tiene cuerpo (no es una notificación de sistema)
            is_livechat_message = rec.model == 'mail.channel' and rec.channel_id.channel_type == 'livechat'
            is_from_customer = rec.author_id != admin_partner
            
            if is_livechat_message and is_from_customer and rec.body:
                
                payload = {
                    "message": rec.body,
                    "author": rec.author_id.name if rec.author_id else "Visitante",
                    "channel_uuid": rec.channel_id.uuid, # Usamos el UUID que es único y accesible
                }
                
                _logger.info(f"LIVECHAT_N8N: Enviando a n8n: {payload}")

                try:
                    r = requests.post(n8n_url, json=payload, timeout=10)
                    r.raise_for_status() # Lanza un error si la respuesta es 4xx o 5xx

                    response_data = r.json()
                    _logger.info(f"LIVECHAT_N8N: Respuesta de n8n: {response_data}")

                    if response_data.get("reply"):
                        # Buscamos el canal por su UUID para responder en el lugar correcto
                        target_channel = self.env['mail.channel'].search([('uuid', '=', rec.channel_id.uuid)], limit=1)
                        if target_channel:
                            target_channel.sudo().message_post(
                                body=response_data["reply"],
                                message_type="comment",
                                subtype_xmlid="mail.mt_comment",
                                author_id=admin_partner.id # La respuesta viene del bot/administrador
                            )
                except requests.exceptions.RequestException as e:
                    _logger.error(f"LIVECHAT_N8N: Error de conexión con n8n: {e}")
                except Exception as e:
                    _logger.error(f"LIVECHAT_N8N: Error inesperado: {e}")

        return records