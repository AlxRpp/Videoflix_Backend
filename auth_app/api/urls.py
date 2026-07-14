from django.urls import path
from .views import RegisterUserView, ActivateUserView, LoginAndSetCookiesView, UserLogoutAndDeleteCookies


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/',
         ActivateUserView.as_view(), name='activate-user'),
    path('login/', LoginAndSetCookiesView.as_view(), name='login'),
    path('logout/', UserLogoutAndDeleteCookies.as_view(), name='logout')
]
