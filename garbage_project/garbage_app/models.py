from django.db import models
from accounts.models import CustomUser

class ActiveManager(models.Manager):
   def get_queryset(self):
      return super().get_queryset().filter(is_active=True)
   
class InactiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)
    
class Location(models.Model):
   name = models.CharField(max_length=100)
   
   def __str__(self):
      return self.name

class CollectionPlan(models.Model):
   """A model for garbage collectors to create a collection plan"""
   class Status(models.TextChoices):
      DAILY= 'DAILY', 'Daily'
      WEEKLY= 'WEEKLY', "Weekly"
      FORTNIGHTLY= 'FORTNIGHTLY', 'Fortnightly'
      MONTHLY= "MONTHLY", 'Monthly'

   garbage_collector = models.ForeignKey('accounts.GarbageCollector', related_name="my_plans", on_delete=models.SET_NULL, null=True)
   status = models.CharField(max_length=40, choices=Status.choices,
                           default=Status.MONTHLY)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   description = models.TextField(blank=True)
   weight=models.PositiveIntegerField(blank=True, null=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at=models.DateTimeField(auto_now=True)
   is_active= models.BooleanField(default=True)
   
   objects = models.Manager()
   active_objects = ActiveManager()
   inactive_objects=InactiveManager()
   
   def __str__(self):
      return f"{self.garbage_collector.user.company_name}"
   
   class Meta:
      ordering=['-updated_at']

class CollectionRequest(models.Model):
   class Status(models.TextChoices):
      PENDING= 'PENDING', 'Pending'
      ACCEPTED= 'ACCEPTED', "Accepted"
      REJECTED= 'REJECTED', 'Rejected'

   garbage_collector= models.ForeignKey('accounts.GarbageCollector', on_delete=models.SET_NULL, null=True)
   customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
   plan = models.ForeignKey(CollectionPlan, on_delete=models.SET_NULL, null=True)
   location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
   address= models.CharField(max_length= 200, blank=False, null=False)
   status = models.CharField(max_length=20, choices= Status.choices, default=Status.PENDING)
   rejection_reason = models.CharField(max_length= 200, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at=models.DateTimeField(auto_now=True)
   is_active= models.BooleanField(default=True)

   objects = models.Manager()
   active_objects = ActiveManager()
   inactive_objects=InactiveManager()
   
   def __str__(self):
      return f"{self.customer.username} - {self.plan.status} - {self.location.name}"
   
   class Meta:
      ordering=['-updated_at']


