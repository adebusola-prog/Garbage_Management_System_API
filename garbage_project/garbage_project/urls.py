from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
# from django.views.generic import RedirectView

from garbage_app.views import CustomUserDocumentView, GarbageCollectorDocumentView, LocationDocumentView

router = routers.SimpleRouter(trailing_slash=False)

router.register(r'customuser-search', CustomUserDocumentView, basename='customuser-search')
router.register(r'garbagecollector-search', GarbageCollectorDocumentView, basename='garbagecollector-search')
router.register(r'location-search', LocationDocumentView, basename='location-search')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/account/", include('accounts.urls', namespace='accounts')),
    path("api/garbage/", include('garbage_app.urls', namespace='garbage')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += router.urls