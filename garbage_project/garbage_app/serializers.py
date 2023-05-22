from .models import CollectionPlan, CollectionRequest, Location
from rest_framework import serializers
from accounts.models import GarbageCollector, CustomUser
from accounts.models import CustomUser
from garbage_app.models import Location
from .documents import CustomUserDocument, GarbageCollectorDocument, LocationDocument
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer


class CustomUserDocumentSerializer(DocumentSerializer):
    class Meta:
        document = CustomUserDocument
        fields = '__all__'

class GarbageCollectorDocumentSerializer(DocumentSerializer):
    class Meta:
        document = GarbageCollectorDocument
        fields = '__all__'

class LocationDocumentSerializer(DocumentSerializer):
    class Meta:
        document = LocationDocument
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Location
        fields=("name",)


class CompanyCustomUserSerializer(serializers.ModelSerializer):
    garbage_collector_location = serializers.SerializerMethodField()

    def get_garbage_collector_location(self, obj):
        return [location.name for location in obj.garbage_collector_location.all()]

    class Meta:
        model = CustomUser
        fields = ("company_name", "garbage_collector_location")


class GarbageCollectorSerializer(serializers.ModelSerializer):
    user=CompanyCustomUserSerializer()    
    class Meta:
        model = GarbageCollector
        fields = ("id", "user", )
        read_only_fields= ['user']


class CollectionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPlan
        fields = ('status', 'price', )
    

class CollectionPlanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPlan
        fields = ('id','status', 'price',)


class GarbageDetailCollectorSerializer(serializers.ModelSerializer):
    user=CompanyCustomUserSerializer()    
    my_plans = CollectionPlanDetailSerializer(many=True, read_only=True)
    class Meta:
        model = GarbageCollector
        fields = ("id", "user", "my_plans")
        read_only_fields= ['user']


class CollectionRequestSerializer(serializers.ModelSerializer):
    plan= CollectionPlanDetailSerializer()
    class Meta:
        model = CollectionRequest
        fields = ('plan', 'address')


class RequestRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['rejection_reason']

class CollectionRequestSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ('plan', 'address')