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
