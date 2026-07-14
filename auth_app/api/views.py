from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from .serializers import RegisterUserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


account_activation_token = AccountActivationTokenGenerator()


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = request.build_absolute_uri(
                f"/api/activate/{uidb64}/{token}/"
            )

            send_mail(
                "Activate your ViedoFlix Account",
                f"Please click on this Link: {activation_link}",
                None,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"user":
                    {
                        "id": user.id,
                        "email": user.email
                    },
                    "token": token},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user_pk = force_str(urlsafe_base64_decode(uidb64))
        try:
            user = User.objects.get(pk=user_pk)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "user not found"}, status=status.HTTP_400_BAD_REQUEST)

        check_token = account_activation_token.check_token(user, token)

        if check_token:
            user.is_active = True
            user.save()
            return Response({
                "message": "Account successfully activated."
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
