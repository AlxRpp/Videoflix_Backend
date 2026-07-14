from django.urls import path
from .views import RegisterUserView, ActivateUserView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/',
         ActivateUserView.as_view(), name='activate-user')
]
