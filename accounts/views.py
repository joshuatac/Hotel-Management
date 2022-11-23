from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from accounts.utils import detectUser

from vendor.forms import VendorForm
from .forms import UserForm
from django.contrib import messages, auth
from .models import User, UserProfile
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


#  Cusotme Decorators for restrict vendor to access customer acc
#  Cusotme Decorators for restrict customer to access vendor acc

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied
    

# Create your views here.

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
       
            #  Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.object.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = User.CUSTOMER
            user.save()

            send_verification_email(request, user)
            messages.error(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)



#  Vendor Registration....

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('dashboard')
    elif request.method == 'POST':
    #   Store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.object.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            
            send_verification_email(request, user)
            messages.success(request, 'Your vendor account has been registered successfully.. Please wait for approval from the Admin side..')
            return redirect('registerVendor')
        else:
            print('The vendor form is Invalid')
            print(form.errors)
    
    else:
        form = UserForm()
        v_form = VendorForm()
    
    context = {
        'form' : form,
        'v_form': v_form,
    }
    
    return render(request, 'accounts/registerVendor.html', context)




def activate(request, uidb64, token):
    # Activate the user by setting the active status to true
    return  



def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('myAccount')
    if request.method == 'POST':
        email = request.POST['email']  # fetching email and password form login page
        password = request.POST['password']
        print(email)
        print(password)        
        #  inbuilt function for login check
        user = auth.authenticate(email=email, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            messages.success(request,' You are logged in..')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,'You are Logged Out..')
    return redirect('login')

@login_required(login_url='login')  # login required decoraters
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login') 
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/cust-dashboard.html')


@login_required(login_url='login') 
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendor-dashboard.html')