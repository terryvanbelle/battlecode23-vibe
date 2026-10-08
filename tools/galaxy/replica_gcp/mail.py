"""EMAIL_BACKEND of the replica: never sends anything (no SMTP, no Mailjet), logs what would have been sent.

siarnaq sends mail only when EMAIL_ENABLED is true (password reset, e-mail verification); the Replica settings keep
it false. This backend is the second fence: even a direct send_mail() goes nowhere.
"""
import logging

from django.core.mail.backends.base import BaseEmailBackend

log = logging.getLogger('siarnaq')


class DropEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for m in email_messages or []:
            log.warning('bc23 replica: e-mail not sent (e-mail is disabled): subject=%r to=%d recipient(s)',
                        getattr(m, 'subject', ''), len(getattr(m, 'to', []) or []))
        return 0
