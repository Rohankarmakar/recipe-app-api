"""Serializers for user api"""
from django.contrib.auth import get_user_model
from rest_framework import (
    serializers,
    authentication,
)

from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """Serializerfor the User Model"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)  # type: ignore

    def update(self, instance, validated_data):
        """Update data and return user."""
        # User may not want to update password but other data
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Validate and Authenticate user"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authentication.authenticate(request=self.context.get('request'),
                                           username=email,
                                           password=password)
        if not user:
            msg = _('Unable to authenticate the provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
