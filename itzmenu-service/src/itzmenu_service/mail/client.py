from typing import Callable

import yagmail

from itzmenu_service.mail.templates import user_verification_email, user_reset_password_email
from itzmenu_service.config.settings import Settings


def send_email(email: str | list[str], subject: str, body_func: Callable[[str], str]):
    settings = Settings()
    body = body_func(settings.service_host)
    yag = yagmail.SMTP(settings.mail_smtp_user, settings.mail_smtp_password,
                       settings.mail_smtp_host, settings.mail_smtp_port,
                       settings.mail_smtp_starttls, settings.mail_smtp_tls,
                       smtp_skip_login=settings.mail_smtp_skip_login)
    yag.send(email, subject, body)
    yag.close()


def send_verification_email(email: str, token: str):
    send_email(email, "Verify your email", lambda host: user_verification_email(token, host))


def send_reset_password_email(email: str, token: str):
    send_email(email, "Reset your password", lambda host: user_reset_password_email(token, host))
