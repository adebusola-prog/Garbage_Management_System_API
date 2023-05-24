from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import GarbageCollector
from .serializers import (
    CollectionPlanSerializer,
    CollectionRequestSerializer,
    GarbageCollectorSerializer,
    RequestRejectionSerializer,
    GarbageDetailCollectorSerializer,
    CollectionRequestSubscribeSerializer,
)
from garbage_app.models import CollectionPlan, CollectionRequest, CustomUser

from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import SearchFilterBackend, FilteringFilterBackend, SuggesterFilterBackend
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from garbage_app.documents import CustomUserDocument, GarbageCollectorDocument, LocationDocument

from .serializers import CustomUserDocumentSerializer, GarbageCollectorDocumentSerializer, LocationDocumentSerializer

class CustomUserDocumentView(DocumentViewSet):
    document = CustomUserDocument
    serializer_class = CustomUserDocumentSerializer

    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend
    ]

    search_fields = (
        'company_name',
        'username',
        'email',
        'garbage_collector_location.name'
    )

    filter_fields = {
        # Add any specific filtering fields if needed
    }

    suggester_fields = {
        'company_name': {
            'field': 'company_name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }

class GarbageCollectorDocumentView(DocumentViewSet):
    document = GarbageCollectorDocument
    serializer_class = GarbageCollectorDocumentSerializer

    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend
    ]

    search_fields = (
        'user.company_name',
        'user.username',
        'user.email',
        'user.garbage_collector_location.name'
    )

    filter_fields = {
        # 
    }

    suggester_fields = {
        'user.company_name': {
            'field': 'user.company_name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }

class LocationDocumentView(DocumentViewSet):
    document = LocationDocument
    serializer_class = LocationDocumentSerializer

    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend
    ]

    search_fields = (
        'name',
    )

    filter_fields = {
        #
    }

    suggester_fields = {
        'name': {
            'field': 'name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }

class CustomerGarbageCollectorsView(APIView):
    """ All the garbage_collectors around a customer's location """
    def get(self, request):
        if request.user.customer_location and not request.user.is_superuser:
            garbage_collectors = GarbageCollector.accepted_collectors.\
                filter(user__garbage_collector_location__name=request.user.customer_location)
            serializer = GarbageCollectorSerializer(garbage_collectors, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No Collector in your location"})
        
class CustomerGarbageCollectorDetailView(APIView):
    """ All the garbage collectors in a customer's location with their respective plans and details"""
    def get_object(self, pk):
        try:
            if self.request.user.customer_location and not self.request.user.is_superuser:
                return GarbageCollector.accepted_collectors.\
                    filter(user__garbage_collector_location__name=self.request.user.customer_location).filter(id=pk).first()
        except GarbageCollector.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        garbage_collector = self.get_object(pk)
        serializer = GarbageDetailCollectorSerializer(garbage_collector)
        return Response(serializer.data)


@api_view(['POST'])
def create_collection_plan(request):
    """ Creating a collection plan """
    if request.method == "POST":
        serializer = CollectionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(garbage_collector=request.user.garbagecollector)
            return Response({"message": "Collection plan created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionPlanListView(APIView):
    """ Listing all specific collection plan """
    def get(self, request):
        plans = CollectionPlan.active_objects.all()
        serializer = CollectionPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollectionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.garbage_collector= request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionPlanDetailView(APIView):
    """ Listing a specific collection plan """
    def get(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        serializer = CollectionPlanSerializer(plan)
        return Response(serializer.data)

    def put(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        serializer = CollectionPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        if plan:
            plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

class AcceptRequestView(APIView):
    """A view for a garbage collector to accept a customer's request"""
    def post(self, request):
        if not request.user.garbage_collector_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)
        if not all_request:
            return Response("No request found", status=status.HTTP_404_NOT_FOUND)
        for request_obj in all_request:
            if request_obj.status in [CollectionRequest.Status.PENDING, CollectionRequest.Status.REJECTED]:
                request_obj.status = CollectionRequest.Status.ACCEPTED
                request_obj.save()
                send_accept_email(request_obj)
                break
        
        redirect_url = reverse('garbage:home_page')
        return Response({"redirect_url": redirect_url}, status=status.HTTP_200_OK)

class RejectRequestView(APIView):
    """A view for a garbage collector to reject a customer's request along with a reason"""
    def post(self, request):
        if not request.user.garbage_collector_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)
        if not all_request:
            return Response("No request found", status=status.HTTP_404_NOT_FOUND)
        for request_obj in all_request:
            serializer = RequestRejectionSerializer(data=request.data, instance=request_obj)
            if serializer.is_valid():
                rejection_reason = serializer.validated_data.get('rejection_reason')
                if request_obj.status in [CollectionRequest.Status.PENDING, CollectionRequest.Status.ACCEPTED]:
                    request_obj.status = CollectionRequest.Status.REJECTED
                    request_obj.rejection_reason = rejection_reason
                    request_obj.save()
                    send_reject_email(request_obj, rejection_reason)
                    break
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        redirect_url = reverse('garbage:home_page')
        return Response({"redirect_url": redirect_url}, status=status.HTTP_200_OK)

class CustomerSubscriptionListView(APIView):
    """A view for customers to see the plan they subscribe to"""
    def get(self, request, pk):
        if request.user.id != pk:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        customer = get_object_or_404(CustomUser.active_objects, customer_location__isnull=False, id=pk)
        all_customer_request = CollectionRequest.active_objects.filter(customer=customer)
        serializer = CollectionRequestSerializer(all_customer_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def send_accept_email(request_obj):
    """Message a customer receives when a subsription is accepted"""
    subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} is now {request_obj.status}"
    message = f"Your request has been accepted and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}"
    send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com', 'aadeyeye@afexnigeria.com'])


def send_reject_email(request_obj, rejection_reason):
    """Message a customer receives when a message is rejected"""
    subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} {request_obj.status}"
    message = f"Your request has been rejected and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}. " \
            f"Reason for rejection: {rejection_reason}"
    send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com', 'aadeyeye@afexnigeria.com'])

class CustomerSubscribe(APIView):
    """Customers Subscribing to a collection plan"""
    def post(self, request, id):
        if not request.user.customer_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        garbage_collector = GarbageCollector.accepted_collectors.filter(user_id=id).first()
        plans = CollectionPlan.active_objects.filter(garbage_collector=garbage_collector)
        serializer = CollectionRequestSubscribeSerializer(data=request.data, instance=plans)
        if serializer.is_valid():
            plan_id = serializer.validated_data.get('plan')
            address = serializer.validated_data.get('address')

            CollectionRequest.objects.create(
                garbage_collector=garbage_collector,
                customer=request.user,
                plan=plan_id,
                location=request.user.customer_location,
                address=address)
            
            return Response({"message": "Collection request created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyCollectionRequestAPIView(APIView):
    """A view for Garbage collectors to see the request made by all their customers"""
    def get(self, request):
        if not request.user.garbage_collector_location:
            return HttpResponseForbidden()
        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)
        if not all_request:
            return Response({"message": "No requests found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CollectionRequestSerializer(all_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


