"""
Serializers for accounts app — registration, login, profile.
"""
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extend JWT payload with basic user info so the
    frontend doesn't need a separate /me/ call on login.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['is_staff'] = user.is_staff
        token['is_author'] = user.is_author
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Append user profile to login response
        data['user'] = UserProfileSerializer(self.user).data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user registration with password confirmation."""
    password = serializers.CharField(
        write_only=True, required=True, min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'password', 'password_confirm',
        ]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only public profile."""
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'avatar_url', 'bio', 'is_author',
            'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Allows users to update their own profile."""
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'bio', 'avatar']

    def validate_avatar(self, value):
        from apps.core.utils import validate_image
        return validate_image(value)


class ChangePasswordSerializer(serializers.Serializer):
    """Handles password change for authenticated users."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'New passwords do not match.'}
            )
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs
