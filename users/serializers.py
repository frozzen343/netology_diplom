from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'address', 'phone']
        read_only_fields = ['id']


class ContactCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'address', 'phone']
        read_only_fields = ['id']
        extra_kwargs = {
            'address': {'required': True},
            'phone': {'required': True}
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True,
                                                  required=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        password_confirmation = validated_data.pop('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError("Пароли не совпадают")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        password_confirmation = validated_data.pop('password_confirmation',
                                                   None)
        if password:
            if password != password_confirmation:
                raise serializers.ValidationError("Пароли не совпадают")
            instance.set_password(password)
        return super().update(instance, validated_data)

    def validate_password(self, value):
        validate_password(value)
        return value

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'password',
                  'password_confirmation', 'email', 'company',
                  'position', 'contacts')
        read_only_fields = ('id', 'contacts')
