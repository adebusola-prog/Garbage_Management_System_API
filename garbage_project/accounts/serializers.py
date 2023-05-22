from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from rest_framework import HTTP_HEADER_ENCODING, authentication

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .models import CustomUser
from garbage_app.models import Location

class LoginSerializer(TokenObtainPairSerializer):
   @classmethod
   def get_token(cls, user):
      token = super().get_token(user)
      # Add custom claims
      token['username'] = user.username
      token['email'] = user.email

      return token

class ResetPasswordSerializer(serializers.ModelSerializer):
   class Meta:
      model = CustomUser
      fields = ('email',)
      extra_kwargs = {
         "email": {
               "write_only": True
         }
      }

   def validate_email(self, value):
      lower_email = value.lower()

      return lower_email

class SetNewPasswordSerializer(serializers.Serializer):
   token = serializers.CharField(min_length=1, write_only=True)
   uuidb64 = serializers.CharField(min_length=1, write_only=True)

   class Meta:
      model = CustomUser
      fields = ("password", "confirm_password", "token", "uuidb64")

   def validate(self, attrs):
      try:
         if attrs.get('password') != attrs.get('confirm_password'):
               raise serializers.ValidationError(
                  {"password": "Password fields didn't match."})
         token = attrs.get('token')
         uuidb64 = attrs.get('uuidb64')

         id = force_str(urlsafe_base64_decode(uuidb64))
         account = CustomUser.objects.get(id=id)

         if not PasswordResetTokenGenerator().check_token(account, token):
               raise AuthenticationFailed('The reset link is invalid', 401)
         account.set_password(attrs.get('password'))
         account.save()
      except Exception as e:
         raise AuthenticationFailed('The reset link is invalid', 401)
      return super().validate(attrs)

class LocationSerializer(serializers.ModelSerializer):
   class Meta:
      model = Location
      fields = ("id", "name",)  

class CompanyRegistrationSerializer(serializers.ModelSerializer):
   password=serializers.CharField(write_only=True, required=True)
   confirm_password = serializers.CharField(write_only=True, required=True)
   company_name = serializers.CharField(required=True)
   garbage_collector_location = LocationSerializer(many=True)

   class Meta:
      model = CustomUser
      fields = ("company_name", "email", "username", "phone_number", "garbage_collector_location", "password", "confirm_password")

   def validate(self, attrs):
      if attrs["password"] != attrs["confirm_password"]:
         raise serializers.ValidationError({"password": "Password fields didn't match."})

      if not attrs["company_name"]:
         raise serializers.ValidationError({"company_name": "Company name is required."})

      if not attrs["garbage_collector_location"]:
         raise serializers.ValidationError({"garbage_collector_location": "Garbage collector location is required."})

      return attrs

class CustomerRegistrationSerializer(serializers.ModelSerializer):
   confirm_password = serializers.CharField(write_only=True, required=True)
   first_name = serializers.CharField(required=True)
   last_name = serializers.CharField(required=True)
   email = serializers.EmailField(required=True)
   password = serializers.CharField(write_only=True, required=True)
   username = serializers.CharField(required=True)
   customer_location = LocationSerializer()

   class Meta:
      model = CustomUser
      fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'username', 'customer_location')

   def validate(self, attrs):
      if attrs['password'] != attrs['confirm_password']:
         raise serializers.ValidationError({"password": "Password fields didn't match."})

      if not attrs['first_name']:
         raise serializers.ValidationError({"first_name": "First name is required."})

      if not attrs['last_name']:
         raise serializers.ValidationError({"last_name": "Last name is required."})

      if not attrs['customer_location']:
         raise serializers.ValidationError({"customer_location": "Customer location is required."})

      return attrs
   
   def create(self, validated_data):
      customer_location = validated_data.pop('customer_location')

class ChangePasswordSerializer(serializers.ModelSerializer):
   new_password = serializers.CharField(
      write_only=True, required=True, validators=[validate_password])
   confirm_password = serializers.CharField(write_only=True, required=True)
   old_password = serializers.CharField(write_only=True, required=True)

   class Meta:
      model = CustomUser
      fields = ('old_password', 'new_password', 'confirm_password')

   def validate(self, attrs):
      if attrs['new_password'] != attrs['confirm_password']:
         raise serializers.ValidationError(
               {"password": "Password fields didn't match."})

      return attrs

   def validate_old_password(self, value):
      user = self.context['request'].user
      if not user.check_password(value):
         raise serializers.ValidationError(
               {"old_password": "Old password is not correct"})
      return value

   def update(self, instance, validated_data):

      instance.set_password(validated_data.get('new_password'))
      instance.save()

      return instance

class CustomerEditSerializer(serializers.ModelSerializer):
   class Meta:
      model = CustomUser
      fields = ("first_name", "email", "middle_name", "last_name", "username",
               "profile_picture", "phone_number", "customer_location")


class MyCompanyEditSerializer(serializers.ModelSerializer):
   class Meta:
      model = CustomUser
      fields = ('username', 'email', 'company_name', 'garbage_collector_location',
               'profile_picture', 'phone_number')
