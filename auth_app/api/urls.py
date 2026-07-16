from django.urls import path
from .views import RegisterUserView, ActivateUserView, LoginAndSetCookiesView, UserLogoutAndDeleteCookies, CookieTokenRefreshView, ResetPasswordView, ConfirmNewPasswordView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/',
         ActivateUserView.as_view(), name='activate-user'),
    path('login/', LoginAndSetCookiesView.as_view(), name='login'),
    path('logout/', UserLogoutAndDeleteCookies.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='refresh-token'),
    path('password_reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('password_confirm/<str:uidb64>/<str:token>/',
         ConfirmNewPasswordView.as_view(), name='new-pasword')
]
