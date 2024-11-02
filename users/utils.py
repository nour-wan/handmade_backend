# utils.py
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(to_email, verification_code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {verification_code}'
    from_email = settings.EMAIL_HOST_USER
    print("From:", from_email)
    print("To:", to_email)
    print("Subject:", subject)
    print("Message:", message)
    
    # send_mail(subject, message, from_email, [to_email])
    try:
        send_mail(subject, message, from_email, [to_email])
    except Exception as e:
        print(f"An error occurred: {e}")
    
import random

def generate_verification_code(length=6):
    # return ''.join(random.randint(100000, 999999))
    
    # Generate a random integer
    code = random.randint(10**(length-1), 10**length - 1)
    # Convert it to a string and return
    return str(code)