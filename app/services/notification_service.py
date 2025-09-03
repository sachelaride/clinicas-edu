
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.tenant_configs import TenantConfig, ConfigKey, ConfigType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_tenant_config(self, tenant_id: uuid.UUID, config_key: ConfigKey) -> str | None:
        result = await self.db.execute(
            select(TenantConfig.config_value)
            .filter_by(tenant_id=tenant_id, config_key=config_key)
        )
        return result.scalars().first()

    async def send_email(
        self,
        tenant_id: uuid.UUID,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ):
        try:
            smtp_host = await self._get_tenant_config(tenant_id, ConfigKey.smtp_host)
            smtp_port_str = await self._get_tenant_config(tenant_id, ConfigKey.smtp_port)
            smtp_user = await self._get_tenant_config(tenant_id, ConfigKey.smtp_user)
            smtp_password = await self._get_tenant_config(tenant_id, ConfigKey.smtp_password)
            smtp_use_ssl_str = await self._get_tenant_config(tenant_id, ConfigKey.smtp_use_ssl)
            smtp_use_tls_str = await self._get_tenant_config(tenant_id, ConfigKey.smtp_use_tls)

            if not all([smtp_host, smtp_port_str, smtp_user, smtp_password]):
                logger.warning(f"Configurações de e-mail incompletas para o tenant {tenant_id}")
                return False

            smtp_port = int(smtp_port_str)
            smtp_use_ssl = smtp_use_ssl_str.lower() == 'true' if smtp_use_ssl_str else False
            smtp_use_tls = smtp_use_tls_str.lower() == 'true' if smtp_use_tls_str else False

            msg = MIMEMultipart("alternative")
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_use_tls:
                    server.starttls()
                if smtp_use_ssl:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            logger.info(f"E-mail enviado com sucesso para {to_email} do tenant {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {to_email} do tenant {tenant_id}: {e}")
            return False

    async def send_sms(self, tenant_id: uuid.UUID, to_phone: str, message: str):
        # This is a placeholder for SMS integration
        # In a real application, you would integrate with an SMS API like Twilio, Nexmo, etc.
        try:
            sms_api_key = await self._get_tenant_config(tenant_id, ConfigKey.sms_api_key)
            sms_sender_id = await self._get_tenant_config(tenant_id, ConfigKey.sms_sender_id)

            if not all([sms_api_key, sms_sender_id]):
                logger.warning(f"Configurações de SMS incompletas para o tenant {tenant_id}")
                return False

            logger.info(f"SMS simulado enviado para {to_phone} do tenant {tenant_id}: {message}")
            # Example of how you might call an external API (pseudo-code)
            # client = SMSClient(api_key=sms_api_key)
            # response = client.send(from_=sms_sender_id, to=to_phone, body=message)
            # if response.success:
            #     return True
            # else:
            #     logger.error(f"Erro na API de SMS: {response.error_message}")
            #     return False
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar SMS para {to_phone} do tenant {tenant_id}: {e}")
            return False
