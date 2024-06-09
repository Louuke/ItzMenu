from email.message import Message
import re

from smtp_test_server.context import SmtpMockServer

from itzmenu_service.mail.client import send_email, send_verification_email, send_reset_password_email

TEST_SEND_EMAIL = 'test_send@example.org'


def test_send_email():
    with SmtpMockServer('127.0.0.1', 42000) as srv:
        assert len(srv.messages) == 0
        send_email(TEST_SEND_EMAIL, 'Test', lambda _: 'Test')
        assert len(srv.messages) == 1
        assert srv.messages[0]['To'] == TEST_SEND_EMAIL


def test_send_verification_email():
    with SmtpMockServer('127.0.0.1', 42000) as srv:
        send_verification_email(TEST_SEND_EMAIL, 'token')
        message: Message = srv.messages[0]
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                pattern = r'/auth/verify\?token=token'
                match = re.search(pattern, part.get_payload(decode=True).decode('utf-8'))
                assert match is not None
                break


def test_send_reset_password_email():
    with SmtpMockServer('127.0.0.1', 42000) as srv:
        send_reset_password_email(TEST_SEND_EMAIL, 'token')
        message: Message = srv.messages[0]
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                pattern = r'/auth/reset-password\?token=token'
                match = re.search(pattern, part.get_payload(decode=True).decode('utf-8'))
                assert match is not None
                break
