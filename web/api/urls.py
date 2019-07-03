from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .views import *

router = routers.DefaultRouter()
router.register(r'artistas', ArtistaViewSet, basename='artistas')
router.register(r'generos', GeneroViewSet, basename='generos')
router.register(r'musicas', MusicaViewSet, basename='musicas')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/', obtain_auth_token, name='obtain_auth_token'),
    path('pesquisa/', PesquisaView.as_view(), name='pesquisa'),
    path('estatisticas/', AdminEstatisticasView.as_view(), name='estatisticas'),
    # path('', include('rest_framework.urls', namespace='rest_framework'))
]
