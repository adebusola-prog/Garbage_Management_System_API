from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
app_name= "garbage"

urlpatterns=[
   path('collectors_customer', views.CustomerGarbageCollectorsView.as_view(), \
        name='collectors_customer_location'),
   path('collectors_detail_customer/<int:pk>/', views.CustomerGarbageCollectorDetailView.as_view(),\
        name="collectors_customer_location"),
   path('customer_subscribe/<int:id>/', views.CustomerSubscribe.as_view(), name="customer_subscribe"),
   path("create_plan", views.create_collection_plan, name="create_plan"),
   path('retreive_collection_request', views.CompanyCollectionRequestAPIView.as_view(), name= "retreive_request"),
   path('accept_request', views.AcceptRequestView.as_view(), name="accept_request"),
   path('reject_request', views.RejectRequestView.as_view(), name="reject_request"),
   path("accept", views.send_accept_email, name="accept_mail"),
   path("reject", views.send_reject_email, name="reject_mail"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])