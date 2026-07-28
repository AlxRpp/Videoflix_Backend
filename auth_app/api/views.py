from django.template.loader import render_to_string
from django.core.mail import send_mail
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import RegisterUserSerializer, CustomLoginSerializer, ResetPasswordSerializer, ConfirmNewPasswordSerializer
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """Include is_active in the hash — the activation token stops working
        once the account is active."""
        return f"{user.pk}{timestamp}{user.is_active}"


account_activation_token = AccountActivationTokenGenerator()


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Create the user and send them an activation link by email."""
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = (
                f"{settings.FRONTEND_URL}/pages/auth/activate.html"
                f"?uid={uidb64}&token={token}"
            )
            html = render_to_string("emails/activation.html", {
                "user": user,
                "activation_link": activation_link,
            })

            send_mail(
                "Confirm your email",
                f"Please click on this link to activate your account:\n\n{activation_link}",
                None,
                [user.email],
                fail_silently=False,
                html_message=html,
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
        """Activate the account if the token from the email is valid."""
        try:
            user_pk = force_str(urlsafe_base64_decode(uidb64))
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


class LoginAndSetCookiesView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        """Log the user in and store the JWT tokens in httpOnly cookies."""
        self.response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data.get('email'))
        access_token = self.response.data.get('access')
        refresh_token = self.response.data.get('refresh')

        try:
            self.response.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                samesite='Lax'
            )

            self.response.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                samesite='Lax'
            )

            self.response.data = {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            }

            return self.response

        except User.DoesNotExist:
            return Response({
                "error": "Invalid Credentials!"
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAndDeleteCookies(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token and delete the auth cookies."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "No refreshtoken in the cookies"
                             }, status=status.HTTP_400_BAD_REQUEST)

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response({"error": "Invalid refresh token "
                             }, status=status.HTTP_400_BAD_REQUEST)

        response = Response({
            "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
        }, status=status.HTTP_200_OK)
        response.delete_cookie(key="refresh_token")
        response.delete_cookie(key="access_token")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        """Hand out a new access token using the refresh token cookie."""
        refresh = request.COOKIES.get("refresh_token")

        if refresh is None:
            return Response({"detail": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"refresh": refresh})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"message": "Token is unvalid"}, status=status.HTTP_401_UNAUTHORIZED)

        accessToken = serializer.validated_data.get("access")

        response = Response({
            "detail": "Token refreshed",
            "access": accessToken
        })

        response.set_cookie(
            key="access_token",
            value=accessToken,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Send a password-reset link to the given email address."""
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(email=request.data.get('email'))
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            reset_link = (
                f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html"
                f"?uid={uidb64}&token={token}"
            )

            html = render_to_string("emails/password_reset.html", {
                "user": user,
                "reset_link": reset_link,
            })

            send_mail(
                "Reset your Password",
                f"Please click on this link to reset your password:\n\n{reset_link}",
                None,
                [user.email],
                fail_silently=False,
                html_message=html,
            )

            return Response(
                {
                    "detail": "An email has been sent to reset your password."
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ConfirmNewPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Set the new password once the reset token checks out."""
        serializer = ConfirmNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_pk = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=user_pk)
            except (User.DoesNotExist, ValueError):
                return Response({"error": "user not found"}, status=status.HTTP_400_BAD_REQUEST)

            check_token = account_activation_token.check_token(user, token)

            if check_token:
                serializer.save(user=user)
                return Response({
                    "detail": "Your Password has been successfully reset."
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
