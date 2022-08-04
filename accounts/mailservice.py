from django.core.mail import send_mail, EmailMultiAlternatives
                            
class Mailservice(object):

    def user_send_mail(mail_parameters):
        
        # try:
            
        mailparameters = mail_parameters
        html_content = f"""<div>Use this code to confirm your mail {mailparameters['otp']}</div>"""
        msg = EmailMultiAlternatives(mailparameters['subject'],"",
                                    mailparameters['sender'], [mailparameters['recipient']])
        msg.attach_alternative(html_content, "text/html")
        mail_status = msg.send() 
        # print("=================>>>>>>> Mailservice sent a single mail")
        return mail_status
            
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