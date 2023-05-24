from django.core.mail import EmailMessage

class Utils:
   @staticmethod
   def send_email(mail_subject, message, email):
      to_email = email
      send_email = EmailMessage(mail_subject, message, to=[to_email])
      send_email.send()
