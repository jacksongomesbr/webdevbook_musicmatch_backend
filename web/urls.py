from django.urls import include, path
from .api import urls as api_urls

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

app_name = 'web'

urlpatterns = [
    path('', include(api_urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]
