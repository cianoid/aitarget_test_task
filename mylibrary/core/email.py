from django.core import mail


def send_email_using_bcc(subject, message, recipient_list, from_email=None,
                         reply_to=None):
    email = mail.EmailMessage(
        subject=subject, body=message, from_email=from_email,
        bcc=recipient_list, reply_to=reply_to)

    email.send(fail_silently=True)
