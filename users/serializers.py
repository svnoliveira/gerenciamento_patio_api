from django.conf import settings
from rest_framework.validators import UniqueValidator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_superuser = serializers.JSONField(required=False, default=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "name",
            "password",
            "is_superuser",
        ]
        depth = 1
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="A user with that username already exists.",
                    )
                ],
            },
            "email": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="user with this email already exists.",
                    )
                ],
            },
        }

    def validate_is_superuser(self, value):

        secret = getattr(settings, "SUPERUSER_CREATION_SECRET", None)
        if secret and value == secret:
            return True
        return False

    def create(self, validated_data: dict) -> User:
        is_superuser = validated_data.pop("is_superuser", False)
        if is_superuser:
            user = User.objects.create_superuser(**validated_data)
        else:
            user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance: User, validated_data: dict) -> User:

        validated_data.pop("is_superuser", None)
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)

        instance.save()

        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs["uid"]).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid reset link"})

        if not PasswordResetTokenGenerator().check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        try:
            validate_password(attrs["new_password"], user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        attrs["user"] = user
        return attrs
