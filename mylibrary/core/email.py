from django.core import mail


def send_email_using_bcc(subject, message, recipient_list, from_email=None,
                         reply_to=None):

    if not from_email or not recipient_list or not message or not subject:
        return False

    email = mail.EmailMessage(
        subject=subject, body=message, from_email=from_email,
        bcc=recipient_list, reply_to=reply_to)

    email.send(fail_silently=True)

    return True
