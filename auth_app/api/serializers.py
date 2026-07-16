from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "username" in self.fields:
            self.fields.pop("username")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {'error': 'Email already exists'})
        return value

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError(
                {'errors': 'Passwords dont match'})
        return value

    def save(self):
        pw = self.validated_data.get('password')
        set_username = self.validated_data.get('email')
        account = User(
            email=self.validated_data['email'], username=set_username, is_active=False
        )
        account.set_password(pw)
        account.save()
        return account


class CustomLoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields.pop('username')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Please enter valid Credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Please enter valid Credentials")

        data = super().validate(
            {"username": user.email,
             "password": password})
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "username" in self.fields:
            self.fields.pop("username")

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {'error': 'Please enter a valid Email'})
        return value


class ConfirmNewPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['new_password', 'confirm_password']

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     if "username" in self.fields:
    #         self.fields.pop("username")

    def validate_confirm_password(self, value):
        password = self.initial_data.get('new_password')
        if password and value and password != value:
            raise serializers.ValidationError(
                {'errors': 'Passwords dont match'})
        return value

    def save(self, **kwargs):
        user = kwargs.get('user')
        pw = self.validated_data.get('new_password')
        user.set_password(pw)
        user.save()
        return user
