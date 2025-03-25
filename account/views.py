from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import BadHeaderError, send_mail
from django.db.models.signals import post_save
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from account.models import User_info, create_user_profile
from agro.models import BeatItem, Notification, Order, ProductItem

from .forms import UserFLEname, UserInfo, UserSignUpForm


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
                return render(request, 'account/login.html')
        else:
            return render(request, 'account/login.html')
    else:
        return redirect('home')


def signup_view(request):
    if not request.user.is_authenticated:
        form = UserSignUpForm()
        form1 = UserInfo()
        if request.method == "POST":
            form = UserSignUpForm(request.POST)
            form1 = UserInfo(request.POST, request.FILES)

            if form.is_valid() and form1.is_valid():
                # Temporarily disconnect the post_save signal
                post_save.disconnect(create_user_profile, sender=User)
                
                try:
                    # Create the user
                    userform = form.save()
                    
                    # Create the User_info record
                    userinfo = form1.save(commit=False)
                    userinfo.user = userform
                    userinfo.save()
                    
                    # Try to send email notification, but don't block account creation if it fails
                    try:
                        from_email = settings.DEFAULT_FROM_EMAIL
                        message = f"Dear {form.cleaned_data['username']}, Thanks for creating an account. Your email address: {form.cleaned_data['email']}"
                        email = form.cleaned_data['email']
                        send_mail(
                            "Your account has been created!", 
                            message, 
                            from_email, 
                            [email], 
                            fail_silently=True
                        )
                    except Exception as e:
                        # Log the error but don't show it to the user
                        print(f"Email sending failed: {str(e)}")
                    
                    messages.success(request, "Account created successfully! Please login with your credentials.")
                    return redirect('login')
                    
                finally:
                    # Reconnect the signal regardless of success or failure
                    post_save.connect(create_user_profile, sender=User)
            else:
                # If forms are not valid, show error messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                
                for field, errors in form1.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")

        return render(request, 'account/signup.html', context={'form': form, 'form1': form1})
    else:
        return redirect('home')

@login_required(login_url='/account/login/')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        if cart := request.session.get('cart'):
            cart = {}
        return redirect('login')
    else:
        return redirect('login')


@login_required(login_url='/account/login/')
def user_profile(request):
    user = request.user
    
    # Try to get user_profile, create if it doesn't exist
    try:
        user_profile = User_info.objects.get(user=user)
    except User_info.DoesNotExist:
        # Create a default User_info for the user
        user_profile = User_info(
            user=user,
            gender='M',  # Default value
            address='Your Address',  # Default value
            phone='Your Phone Number',  # Default value
            user_type='B',  # Default as Buyer
            profile_pic='profilepic/default.jpg'  # Using default profile pic
        )
        user_profile.save()
        messages.info(request, "We've created a default profile for you. Please update your information.")
    
    products = ProductItem.objects.filter(user=user)
    beat_item = BeatItem.objects.filter(user=user)
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-create_date')[:5]
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-create_date')[:10]
    
    context = {
        'user': user,
        'profile': user_profile,
        'products': products,
        'beat_items': beat_item,
        'recent_orders': recent_orders,
        'notifications': notifications
    }
    return render(request, 'account/dashboard.html', context)


@login_required(login_url='/account/login/')
def editUserInfo(request):
    user = User.objects.get(username=request.user.username)
    
    # Try to get user_profile, create if it doesn't exist
    try:
        mydata = User_info.objects.get(user=request.user)
    except User_info.DoesNotExist:
        # Create a default User_info for the user
        mydata = User_info(
            user=request.user,
            gender='M',  # Default value
            address='Your Address',  # Default value
            phone='Your Phone Number',  # Default value
            user_type='B',  # Default as Buyer
            profile_pic='profilepic/default.jpg'  # Using default profile pic
        )
        mydata.save()
        messages.info(request, "We've created a default profile for you. Please update your information.")
    
    if request.method == 'POST':
        # Make sure to use request.FILES for file uploads
        form = UserInfo(request.POST, request.FILES, instance=mydata)
        form1 = UserFLEname(request.POST, instance=user)
        
        if form.is_valid() and form1.is_valid():
            # Debug information
            print(f"Form data: {form.cleaned_data}")
            print(f"Form1 data: {form1.cleaned_data}")
            
            # Save the forms
            form.save()
            form1.save()
            
            messages.success(request, "Profile updated successfully!")
        else:
            # If forms are not valid, show error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            
            for field, errors in form1.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
        
        return redirect('userprofile')
    else:
        form = UserInfo(instance=mydata)
        form1 = UserFLEname(instance=user)
    
    context={
        'form': form,
        'form1': form1,
        'userinfo': mydata,
    }
    return render(request, 'account/editinfo.html', context)


@login_required(login_url='/account/login/')
def delete_account(request):
    if request.method == "POST":
        user = request.user
        try:
            # This will delete the User and all related data due to CASCADE
            user.delete()
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('home')
        except Exception as e:
            messages.error(request, "An error occurred while deleting your account. Please try again.")
            return redirect('editUserInfo')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('editUserInfo')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    subject_template_name = 'account/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')