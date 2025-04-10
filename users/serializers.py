from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(max_length=100, write_only=True)
    password2 = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')