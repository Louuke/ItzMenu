import re
from pathlib import Path
from typing import Any

import yagmail

from itzmenu_service.config.settings import Settings


class MailTemplate:

    def __init__(self, subject: str, template_name: str, placeholders: dict[str, Any] = None):
        """
        Wrapper class for email templates.

        :param subject: Subject of the email
        :param template_name: Name of the template file
        :param placeholders: Dictionary with placeholders for the template
        """
        self.__subject = subject
        self.__template_name = template_name
        placeholders = placeholders if placeholders else {}
        self.__placeholders = Settings().model_dump() | placeholders

    def to_html(self) -> str:
        """
        Load the template and replace placeholders with values.

        :return: HTML content of the template
        """
        return self.__load_and_replace()

    @property
    def subject(self) -> str:
        """
        Get the subject of the email.

        :return: Subject of the email
        """
        return self.__subject

    def __replacements(self) -> dict[str, Any]:
        return {'{{ ' + key + ' }}': value for key, value in self.__placeholders.items()}

    def __load_and_replace(self) -> str:
        replacements = self.__replacements()
        file = Path(__file__).parent / f'templates/{self.__template_name}.html'
        with open(file, 'r') as f:
            content = f.read()
            pattern = re.compile("|".join(map(re.escape, replacements.keys())))
            content = pattern.sub(lambda match: replacements[match.group(0)], content)
        return content


class SMTPClient:

    def __init__(self):
        """
        Wrapper class for sending emails using SMTP.
        """
        self.__settings = Settings()
        self.__yag = yagmail.SMTP(self.__settings.mail_smtp_user, self.__settings.mail_smtp_password,
                                  self.__settings.mail_smtp_host, self.__settings.mail_smtp_port,
                                  self.__settings.mail_smtp_starttls, self.__settings.mail_smtp_tls,
                                  smtp_skip_login=self.__settings.mail_smtp_skip_login)

    def send_email(self, email: str | list[str], template: MailTemplate):
        """
        Send an email using the SMTP client.

        :param email: Recipient email address
        :param template: Email template
        :return: None
        """
        self.__yag.send(email, template.subject, template.to_html())

    def send_verification_email(self, email: str, token: str):
        """
        Send a verification email.

        :param email: Recipient email address
        :param token: Verification token
        :return: None
        """
        template = MailTemplate("Verify your email", "verify", {"token": token})
        self.send_email(email, template)

    def send_reset_password_email(self, email: str, token: str):
        """
        Send a reset password email.

        :param email: Recipient email address
        :param token: Reset password token
        :return: None
        """
        template = MailTemplate("Reset your password", "reset", {"token": token})
        self.send_email(email, template)
