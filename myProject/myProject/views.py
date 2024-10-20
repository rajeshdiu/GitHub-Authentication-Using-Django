
from django.conf import settings
import uuid
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myApp.models import *
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import PasswordResetForm
from myProject.forms import *

from django.http import HttpResponse
from django.utils.encoding import force_str  # Change this line
from django.contrib.auth import update_session_auth_hash

from django.utils.http import urlsafe_base64_decode

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def signupPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        confirm_password = request.POST['confirm-password']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        user_type = request.POST.get('user_type')

        if password == confirm_password:
            if Custom_User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signupPage')
            elif Custom_User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return redirect('signupPage')
            else:
                user = Custom_User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type,
                )
                user.save()
                auth_token = str(uuid.uuid4())
                user.auth_token = auth_token
                user.save()
                
                send_mail_after_registration(email , auth_token)
                return redirect('send_token')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('signupPage')

    return render(request, 'signupPage.html')


def send_mail_after_registration(email,token):
    print("Mail Sent")
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )
    


def send_token(request):
    
    return render(request,"send_token.html")

def error_page(request):
    return  render(request , 'error.html')


def successPage(request):
    
    return render(request,"successPage.html")


def verify(request,auth_token):
    
    print("Mail Verified")
    try:
        user_obj = Custom_User.objects.filter(auth_token = auth_token).first()

        if user_obj:
            if user_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('signInPage')
            user_obj.is_verified = True
            user_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('signInPage')
        else:
            return redirect('signInPage')
    except Exception as e:
        print(e)
        return redirect('/')



# Signin View
def signInPage(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = Custom_User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('homePage') 
            else:
                messages.error(request, 'Invalid credentials, please try again.')
                return redirect('signInPage')

        except Custom_User.DoesNotExist:
            messages.error(request, 'No user with this email exists.')
            return redirect('signInPage')

    return render(request, 'signInPage.html')

# Signout View
def logoutPage(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('signInPage')

@login_required
def homePage(request):
    
    return render(request,"homePage.html")


def password_reset_request(request):
    print("Password Reset")

    if request.method == "POST":
        print("Inside Password Reset and POST")

        email = request.POST.get('email')
        
        associated_users = Custom_User.objects.filter(Q(email=email))
        
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "password/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'your_email@example.com', [user.email], fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')

            return redirect("password_reset_done") 
    return render(request, "password/password_reset.html")  # Render the custom form template



def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  # Change this line
        user = Custom_User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Custom_User.DoesNotExist):
        user = None

    if request.method == "POST":
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 and new_password1 == new_password2:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after changing the password
            return redirect('password_reset_complete')  # Redirect to a completion page

    return render(request, "password/password_reset_confirm.html", {"user": user})


def password_reset_done(request):
    return render(request, "password/password_reset_done.html")

def password_reset_complete(request):
    return render(request, "password/password_reset_complete.html")
