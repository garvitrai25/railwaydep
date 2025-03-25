from django.urls import include, path

from .views import (ResetPasswordView, delete_account, editUserInfo,
                    signup_view, user_login, user_logout, user_profile)

urlpatterns = [
    path('login/', user_login, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('userprofile/', user_profile, name='userprofile'),
    path('editUserInfo/', editUserInfo, name='editUserInfo'),
    path('delete-account/', delete_account, name='delete_account'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),

    path('', include('django.contrib.auth.urls')),
]
