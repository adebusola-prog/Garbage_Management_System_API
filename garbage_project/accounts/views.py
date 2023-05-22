from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView

from .renderers import CustomRenderer
from .serializers import (
    ChangePasswordSerializer,
    CompanyRegistrationSerializer,
    CustomerEditSerializer,
    CustomerRegistrationSerializer,
    MyCompanyEditSerializer,
    ResetPasswordSerializer,
)
from accounts.models import CustomUser
from garbage_app.models import Location
from .serializers import (
    LoginSerializer,
    SetNewPasswordSerializer,
    LocationSerializer,
)


class LogoutView(APIView):
   def post(self, request, *args, **kwargs):
      request.user.auth_token.delete()
      return Response(status=status.HTTP_200_OK)

class LoginView(TokenObtainPairView):
   serializer_class = LoginSerializer
   renderer_classes = [CustomRenderer]

class ChangePasswordAV(generics.UpdateAPIView):
   queryset = CustomUser.objects.all()
   serializer_class = ChangePasswordSerializer

class CustomerRegistrationView(generics.CreateAPIView):
   serializer_class = CustomerRegistrationSerializer
   renderer_classes = [CustomRenderer]

   def post(self, request, *args, **kwargs):
      serializer = CustomerRegistrationSerializer(data=request.data)
      data = {}
      print(serializer.is_valid())
      if serializer.is_valid():
         username = serializer.validated_data.get("username")
         first_name = serializer.validated_data.get("first_name")
         last_name = serializer.validated_data.get("last_name")
         email = serializer.validated_data.get("email")
         print(email)
         # location_id = serializer.validated_data.get("customer_location")["id"]
         print(serializer.data)
         location_name = serializer.validated_data.get("customer_location").get("name")
         print(location_name)
         location = get_object_or_404(Location, name=location_name)
         print(location)
         # print(location)
         password = serializer.validated_data.get("password")
         # confirm_password = serializer.validated_data.get("password2")
         account = CustomUser.objects.create_user(
               first_name=first_name, last_name=last_name, username=username, customer_location=location, email=email, password=password)
         data["status"] = "success"
         data["username"] = account.username
         data["email"] = account.email
         refresh_token = RefreshToken.for_user(account)
         data["refresh_token"] = str(refresh_token)
         data["access_token"] = str(refresh_token.access_token)
         return Response(data, status=status.HTTP_201_CREATED)
      data["error"] = serializer.errors
      data["status"] = "success"
      return Response(data, status=status.HTTP_400_BAD_REQUEST)

class CompanyRegistrationView(generics.CreateAPIView):
   serializer_class = CompanyRegistrationSerializer
   renderer_classes = [CustomRenderer]

   def post(self, request, *args, **kwargs):
      serializer = CompanyRegistrationSerializer(data=request.data)
      data = {}
      print(serializer.is_valid())
      if serializer.is_valid():
         username = serializer.validated_data.get("username")
         company_name = serializer.validated_data.get("company_name")
         phone_number = serializer.validated_data.get("phone_number")
         email = serializer.validated_data.get("email")
         garbage_collector_locations = serializer.validated_data.get("garbage_collector_location")
         # print(garbage_collector_locations)
         password = serializer.validated_data.get("password")
         # confirm_password = serializer.validated_data.get("password2")
            
         account = CustomUser.objects.create_user(
               company_name=company_name, phone_number=phone_number, username=username, email=email, password=password)
         # Create garbage collector locations
         for location in garbage_collector_locations:
            garbage_collector_location = Location.objects.create(name=location.get("name"))
            account.garbage_collector_location.set([garbage_collector_location])

         data["status"] = "success"
         data["username"] = account.username
         data["email"] = account.email
         refresh_token = RefreshToken.for_user(account)
         data["refresh_token"] = str(refresh_token)
         data["access_token"] = str(refresh_token.access_token)
         messages.success(request, "Thank you for signing up! You will be contacted shortly if your registration is approved.")
         return Response(data, status=status.HTTP_201_CREATED)
      data["error"] = serializer.errors
      data["status"] = "success"
      return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ForgotPassordAV(APIView):
   serializer_class = ResetPasswordSerializer

   def post(self, request, *args, **kwargs):

      serializer = self.serializer_class(data=request.data)
      serializer.is_valid(raise_exception=True)
      lower_email = serializer.validated_data.get("email").lower()
      if CustomUser.objects.filter(email__iexact=lower_email).exists():
         account = CustomUser.objects.get(email=lower_email)
         uuidb64 = urlsafe_base64_encode(account.id)
         token = PasswordResetTokenGenerator().make_token(account)
         current_site = get_current_site(
               request).domain
         relative_path = reverse(
               "reset-password", kwargs={"uuidb64": uuidb64, "token": token})
         abs_url = "http://" + current_site + relative_path

         mail_subject = "Please Reset your CustomUser Password"
         message = "Hi" + account.username + "," + \
               " Please Use the Link below to reset your account passwors:" + "" + abs_url

         Utils.send_email(mail_subject, message, account.email)
      return Response({"status": "success", "message": "We have sent a password-reset link to the email you provided.Please check and reset  "}, status=status.HTTP_200_OK)


class ResetPassordAV(APIView):
   serializer_class = ResetPasswordSerializer
   renderer_classes = [CustomRenderer]

   def get(self, request, uuidb64, token):
      try:
         id = smart_str(urlsafe_base64_decode(uuidb64))
         account = CustomUser.objects.get(id=id)
         if not PasswordResetTokenGenerator().check_token(account, token):
               return Response({"status": "fail", "message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
         return Response({"status": "success", "message": "Your credentials valid", "uuidb64": uuidb64, "token": token}, status=status.HTTP_400_BAD_REQUEST)
      except DjangoUnicodeDecodeError as e:
         return Response({"status": "fail", "message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordAV(generics.GenericAPIView):
   serializer_class = SetNewPasswordSerializer
   renderer_classes = [CustomRenderer]

class CustomerEditView(UpdateAPIView):
    serializer_class = CustomerEditSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(username=self.request.user.username)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"status": "success", "message": "Password was successfully reset"}, status=status.HTTP_200_OK)



class MyCompanyEditView(generics.UpdateAPIView):
   serializer_class = MyCompanyEditSerializer
   queryset = CustomUser.objects.all()


class ListCreateLocationView(generics.ListCreateAPIView):
   serializer_class= LocationSerializer
   queryset= Location.objects.all()