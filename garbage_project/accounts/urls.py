from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from garbage_app.models import Location

app_name = "accounts"

urlpatterns=[
   path('login', views.LoginView.as_view(), name='login'),
   
   path('location', views.ListCreateLocationView.as_view(), name="location_create"),
   path('customer/register', views.CustomerRegistrationView.as_view(), name='customer_register'),
   path('customer/<int:pk>/edit', views.CustomerEditView.as_view(), name='customer_edit'),
   path('company/register', views.CompanyRegistrationView.as_view(), name='company_register'),
   path('logout/', views.LogoutView.as_view(), name='logout'),
   path('change-password/<int:pk>/', views.ChangePasswordAV.as_view(),
      name='change-password'),
   path('forgot-password/<int:pk>/', views.ForgotPassordAV.as_view(),
      name='forgot-password'),
   path('reset-password/<int:uuidb64>/<token>/', views.ResetPassordAV.as_view(),
      name='reset-password'),
   path('password-reset-complete/', views.SetNewPasswordAV.as_view(),
      name='password-reset-complete'),


]
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])