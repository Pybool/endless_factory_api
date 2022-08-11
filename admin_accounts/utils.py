import time
import base64
from django.core.mail import EmailMultiAlternatives, message
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_mail(from_email, to_email, subject, body, type, sender_name, phone_number):

    subject= subject
    html_content = render_to_string(
        "contact-us.html",
        {
            "sender_email": from_email,
            "sender_name": sender_name,
            "body": body,
            "subject": subject,
            "type": type
        },
    )
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return True