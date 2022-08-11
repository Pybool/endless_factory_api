from django.core.mail import send_mail, EmailMultiAlternatives
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
                            
class Mailservice(object):

    def user_send_mail(mail_parameters):
        
        # try:
            
        mailparameters = mail_parameters
        html_content = f"""<div>Use this code to confirm your mail {mailparameters['otp']}</div>"""
        # msg = EmailMultiAlternatives(mailparameters['subject'],"",
        #                             mailparameters['sender'], [mailparameters['recipient']])
        # msg.attach_alternative(html_content, "text/html")
        # mail_status = msg.send() 
        # print("=================>>>>>>> Mailservice sent a single mail")
        # return mail_status
        Mailservice.send_message(html_content)
            
        # except Exception as e:
        #     print("An error ocurred while sending mail ",e)
            
    def pass_reset_send_mail(mail_parameters):
        
        try:
            
            mailparameters = mail_parameters
            html_content = f"""<a href='{mailparameters['url']}'>Click to reset your password</a>"""
            msg = EmailMultiAlternatives(mailparameters['subject'],"",
                                        mailparameters['sender'], [mailparameters['recipient']])
            msg.attach_alternative(html_content, "text/html")
            mail_status = msg.send() 
            # print("=================>>>>>>> Mailservice sent a single password reset mail")
            return mail_status
            
        except Exception as e:
            print("An error ocurred while sending mail ",e)
            

    def send_message(html_content):

        message = Mail(
            from_email='endlessfactory.co.uk',
            to_emails='ekoemmanueljavl@gmail.com',
            subject='Sending with Twilio SendGrid is Fun',
            html_content= html_content)
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)