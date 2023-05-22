from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from .models import Location
from accounts.models import GarbageCollector

@receiver(post_save)
def update_document(sender, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']

    if app_label == 'accounts':
        if model_name == 'customuser':
            registry.update(instance)
        elif model_name == 'garbagecollector':
            registry.update(instance)

@receiver(post_delete)
def delete_document(sender, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']

    if app_label == 'accounts':
        if model_name == 'customuser':
            registry.update(instance)
        elif model_name == 'garbagecollector':
            registry.update(instance)

# @receiver(post_save)
# def update_document(sender, **kwargs):
#     app_label = sender._meta.app_label
#     model_name = sender._meta.model_name
#     instance = kwargs['instance']

#     if app_label == 'garbage_app':
#         if model_name == 'location':
#             registry.update(instance)
        

# @receiver(post_delete)
# def delete_document(sender, **kwargs):
#     app_label = sender._meta.app_label
#     model_name = sender._meta.model_name
#     instance = kwargs['instance']

#     if app_label == 'garbage_app':
#         if model_name == 'location':
#             registry.update(instance)
        
