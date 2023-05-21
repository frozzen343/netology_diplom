from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

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


class EmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        token = attrs.get('token')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        if not Token.objects.filter(user=user, key=token).exists():
            raise serializers.ValidationError("Invalid token.")

        user.is_active = True
        user.save()

        return attrs


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        "Пользователь неактивен.")
            else:
                raise serializers.ValidationError("Неверные учетные данные.")
        else:
            raise serializers.ValidationError(
                "Необходимо предоставить электронную почту и пароль.")

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True,
                                                  required=True)

    def create(self, validated_data):
        password = validated_data.get('password')
        password_confirmation = validated_data.pop('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError("Пароли не совпадают")
        user = User.objects.create_user(**validated_data)
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
