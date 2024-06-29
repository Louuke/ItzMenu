from email.message import Message
import re

from smtp_test_server.context import SmtpMockServer

from itzmenu_service.config.settings import Settings
from itzmenu_service.mail.client import SMTPClient, MailTemplate

TEST_SEND_EMAIL = 'test_send@example.org'


class TestSMTPClient:

    def test_send_email(self):
        client = SMTPClient()
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            assert len(srv.messages) == 0
            template = MailTemplate('Test', 'verify')
            client.send_email(TEST_SEND_EMAIL, template)
            assert len(srv.messages) == 1
            assert srv.messages[0]['To'] == TEST_SEND_EMAIL

    def test_send_verification_email(self):
        client = SMTPClient()
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            client.send_verification_email(TEST_SEND_EMAIL, 'token')
            message: Message = srv.messages[0]
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    pattern = r'/auth/verify\?token=token'
                    match = re.search(pattern, part.get_payload(decode=True).decode('utf-8'))
                    assert match is not None
                    break

    def test_send_reset_password_email(self):
        client = SMTPClient()
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            client.send_reset_password_email(TEST_SEND_EMAIL, 'token')
            message: Message = srv.messages[0]
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    pattern = r'/auth/reset-password\?token=token'
                    match = re.search(pattern, part.get_payload(decode=True).decode('utf-8'))
                    assert match is not None
                    break


class TestMailTemplate:

    def test_verification_to_html(self):
        settings = Settings()
        template = MailTemplate('Subject', 'verify', {'token': 'jwt_token'})
        html = template.to_html()
        assert 'confirm email' in html
        assert f'{settings.service_public_address}/auth/verify?token=jwt_token' in html
        assert template.subject == 'Subject'

    def test_reset_to_html(self):
        settings = Settings()
        template = MailTemplate('Subject', 'reset', {'token': 'jwt_token'})
        html = template.to_html()
        assert 'reset password' in html
        assert f'{settings.service_public_address}/auth/reset-password?token=jwt_token' in html
        assert template.subject == 'Subject'
