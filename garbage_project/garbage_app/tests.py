from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from decouple import config

from accounts.models import CustomUser, GarbageCollector
from .models import CollectionPlan, CollectionRequest, Location

class CollectionPlanSubscriptionTest(APITestCase):
    @classmethod
    def setUp(cls):
        location= Location.objects.get_or_create(id= 1, name="Ibadan")
        customer, x = CustomUser.active_objects.get_or_create(
            email="tugrp@example.com", 
            first_name= "Ola",
            last_name= "Ope",
            username= "Orru",
            password= "aferekdk5687A",
            # confirm_password= "aferekdk5687A",
            # customer_location= {"pk":1}

        )
        
        return location, customer
   
    
    @property
    def get_token(self):
        return RefreshToken.for_user(self.setUp()).access_token


    def test_collection_plan_subscription_create(self):
        self.client.login(email="tugrp@example.com", password="aferekdk5687A")
        url= reverse("garbage:customer_subscribe", args=["1"])
        response= self.client.get(url)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
