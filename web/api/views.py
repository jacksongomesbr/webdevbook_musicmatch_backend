from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib import auth

from .serializers import *
from ..models import *


class LoginView(APIView):
    """
    A view LoginView trata da funcionalidade de autenticação do usuário.
    """

    permission_classes = [permissions.AllowAny, ]
    """Qualquer requisição para esta view está autorizada"""

    def post(self, request):
        """
        Este método implementa a autenticação do usuário.

        É obrigatório que o corpo da requisição contenha as chaves `username` e `password`, que representam,
        respectivamente, o nome e a senha do usuário.

        De posse dessas informações (credenciais) o código utiliza a autenticação do django (classe `auth`)
        e o resultado é utilizado para identificar se a autenticação foi bem sucedida ou não.

        Se tiver sido bem sucedida, o método retorna uma resposta HTTP de código 200 contendo a seguinte estrutura:

        * atributo `user` (dict): o conteúdo é a representação do objeto `User` associado ao usuário em questão,
        serializado pela classe `UserModelSerializer`
        * atributo `token` (str): contém o token do usuário

        Se não houver sucesso na autenticação o método retorna uma resposta HTTP de código 403 e nenhum
        conteúdo na resposta.

        :param request: A requisição HTTP
        :return: Um objeto represntando o resultado da autenticação
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            # auth.login(request, user)
            serializer = UserModelSerializer(user, many=False)
            return Response({'user': serializer.data, 'token': str(token)}, status=200)
        else:
            return Response(None, status=403)


class AdminEstatisticasView(APIView):
    # permission_classes = [permissions.IsAdminUser]
    """Só permite acessar essa view se o usuário estiver autenticado e for admin"""

    def get(self, request):
        result = {
            'musicas': Musica.objects.count(),
            'artistas': Artista.objects.count(),
            'generos': Genero.objects.count()
        }

        return Response(result, status=200)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        auth.logout(request)
        return Response(None, status=200)


class ArtistaViewSet(viewsets.ModelViewSet):
    """
    A view `ArtistaViewSet` implementa o acesso ao model `Artista`
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    queryset = Artista.objects.all()
    """O queryset representa todos os artistas"""

    serializer_class = ArtistaSerializer
    """A classe de serialização é a `ArtistaSerializer`"""

    search_fields = ['nome']
    """O cliente pode fazer busca pelo campo nome"""

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    """O cliente pode aplicar filtros conforme os campos, além de pesquisa e de ordenação"""

    ordering_fields = ['nome']
    """Os campos que podem ordenar o resultado"""

    @action(detail=True, methods=['post'])
    def remover_foto(self, request, pk=None):
        """
        Esta ação, disponível via POST, remove a foto do artista.
        O procedimento realizado é o seguinte:

        1. obtém o objeto/registro do artista
        2. define `None` para a `foto`
        3. salva o objeto/registro

        :param request:
        :param pk: O identificador do artista
        :return:
        """
        try:
            artista = self.get_object()
            artista.foto = None
            artista.save()
            ser = self.get_serializer(artista, many=False)
            return Response(ser.data, status=status.HTTP_200_OK)
        except:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


class GeneroViewSet(viewsets.ModelViewSet):
    """A view `GeneroViewSet` implementa o acesso ao model `Genero`"""

    queryset = Genero.objects.all()
    """O queryset representa todos os gêneros"""

    serializer_class = GeneroSerializer
    """A classe de serialização é `GeneroSerializer`"""

    search_fields = ['nome']
    """O cliente pode fazer busca pelo campo nome"""

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    """O cliente pode aplicar filtros conforme os campos, além de pesquisa e de ordenação"""

    ordering_fields = ['nome']
    """Os campos que podem ordenar o resultado"""


class MusicaViewSet(viewsets.ModelViewSet):
    """A view `MusicaViewSet` implementa o acesso ao model `Musica`"""

    queryset = Musica.objects.all()
    """O queryset representa todas as músicas"""

    serializer_class = MusicaSerializer
    """A classe de serialização é `MusicaSerializer`"""

    filterset_fields = ['genero', 'artistas']
    """O cliente pode filtrar pelo gênero e pelos artistas"""

    search_fields = ['titulo', 'letra', 'genero__nome', 'artista__nome']
    """O cliente pode fazer busca pelos campos: título, letra, nome do gênero e nome do artista"""

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    """O cliente pode aplicar filtros conforme os campos, além de pesquisa e de ordenação"""

    @action(detail=True, methods=['post'])
    def gostar(self, request, pk=None):
        try:
            musica = self.get_object()
            if musica.gostar is not None:
                musica.gostar += 1
            else:
                musica.gostar = 1
            musica.save()
            ser = self.get_serializer(musica, many=False)
            return Response(ser.data, status=status.HTTP_200_OK)
        except:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def nao_gostar(self, request, pk=None):
        try:
            musica = self.get_object()
            if musica.naoGostar is not None:
                musica.naoGostar += 1
            else:
                musica.naoGostar = 1
            musica.save()
            ser = self.get_serializer(musica, many=False)
            return Response(ser.data, status=status.HTTP_200_OK)
        except:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


class PesquisaView(APIView):
    """A view `PesquisaView` implementa a funcionalidade de pesquisa"""

    def get(self, request):
        """
        Este método implementa o acesso aos dados (via GET).

        O código obtém o valor do parâmetro de URL `search` e:

        * se disponível
            * busca as músicas cujos título ou letra contêm parte do parâmetro `search`
            * busca os artistas cujos nome contêm parte do parâmetro `search`
            * busca os generos cujos nome contêm parte do parâmetro `search`
            * serializa as listas
            * retorna uma resposta HTTP com código 200 e a seguinte estrutura:
                * atributo `results` contém os atributos `musicas`, `artistas` e `generos`, que contêm as listas correspondentes
        * caso contrário
            * retorna uma resposta HTTP com código 200 e a mesma estrutura indicada antes, mas com `None` ao invés das listas, indicando ue nào houve, resultado que combinasse com o parâmetro de busca

        :param request: A requisição HTTP
        :return:
        """
        search = self.request.query_params.get('search', None)
        if search is not None:
            musicas = Musica.objects.filter(Q(titulo__icontains=search) | Q(letra__icontains=search))
            artistas = Artista.objects.filter(nome__icontains=search)
            generos = Genero.objects.filter(nome__icontains=search)

            musicas_data = MusicaSerializer(musicas, many=True).data
            artista_data = ArtistaSerializer(artistas, many=True).data
            generos_data = GeneroSerializer(generos, many=True).data

            return Response({'results': {
                'musicas': musicas_data,
                'artistas': artista_data,
                'generos': generos_data
            }}, 200)
        else:
            return Response({'results': {'musicas': None,
                                         'artistas': None,
                                         'generos': None}}, 200)
