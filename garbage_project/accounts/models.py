from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse

from phonenumber_field.modelfields import PhoneNumberField

class InactiveManager(models.Manager):
   
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)
    
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class AcceptedGarbageCollector(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_accepted=True)
   
class UnacceptedGarbageCollector(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_accepted=False)

class CustomUser(AbstractUser):
    """ User's sign_up fields for authentication"""
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    referral_code=models.CharField(max_length=5, blank=True, null=True)
    company_name= models.CharField(max_length=100, unique=True, blank=True, null=True)
    username = models.CharField(max_length=19, unique=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to="user_profile_picture", default="avatar.svg")
    customer_location= models.ForeignKey('garbage_app.Location', on_delete=models.SET_NULL, null=True, blank=True)
    garbage_collector_location=models.ManyToManyField('garbage_app.Location', related_name='my_locations', blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, )
    is_active = models.BooleanField(default=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    

    def __str__(self):
        return self.username
    
    @property
    def image_URL(self):
        try:
            url= self.profile_picture.url
        except:
            url= ''
        return url
    
class GarbageCollector(models.Model):
    """Garbage Collectors model after signing up"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    is_accepted= models.BooleanField(default=False)

    objects=models.Manager()
    accepted_collectors=AcceptedGarbageCollector()
    unaccepted_collectors=UnacceptedGarbageCollector()

    def __str__(self):
        return self.user.username
            
    
class CustomerProfile(models.Model):
    """Customer's profile after signing up"""
    account = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
      return self.account.username