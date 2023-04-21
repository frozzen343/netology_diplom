from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'address', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'address': {'required': True},
            'phone': {'required': True},
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
            if validated_data.get('password'):
                instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def validate(self, attrs):
        if attrs.get('password1') and attrs.get('password2'):
            try:
                validate_password(attrs['password1'])
            except ValidationError as err:
                raise serializers.ValidationError({'password1': err})

            if attrs['password1'] != attrs['password2']:
                raise serializers.ValidationError(
                    {'password2': "Пароли не совпадают"})

            attrs['password'] = attrs['password1']
            del attrs['password1']
            del attrs['password2']
        return attrs

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'password1',
                  'password2', 'email', 'company', 'position',
                  'contacts')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password1': {'required': True},
            'password2': {'required': True},
            'company': {'required': True},
            'position': {'required': True},
        }
        read_only_fields = ('id',)
