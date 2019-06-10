from ..models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class PermissionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserModelSerializer(serializers.ModelSerializer):
    user_permissions = PermissionModelSerializer(many=True)

    class Meta:
        model = User
        fields = ['email', 'groups', 'id', 'is_superuser', 'last_login', 'date_joined', 'user_permissions', 'username']


class ModelSerializerValidateMixin:
    # def validate(self, attrs):
    #     self.Meta.model.objects.is_valid(self.Meta.model(**attrs))
    #     return attrs

    def validate(self, attrs):
        instance = self.Meta.model(**attrs)
        instance.clean()
        return attrs


class MusicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musica
        fields = '__all__'


class ArtistaSerializer(ModelSerializerValidateMixin, serializers.ModelSerializer):
    class Meta:
        model = Artista
        fields = '__all__'

    #
    # def validate(self, attrs):
    #     Artista.objects.is_valid(Artista(**attrs))
    #     return attrs
    musicas = MusicaSerializer(many=True, read_only=True)


class GeneroSerializer(ModelSerializerValidateMixin, serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

    musicas = MusicaSerializer(many=True, read_only=True)


class MusicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musica
        fields = '__all__'

    genero_id = serializers.PrimaryKeyRelatedField(required=True, write_only=True, queryset=Genero.objects.all())
    genero = GeneroSerializer(read_only=True)
    artistas = ArtistaSerializer(many=True, read_only=True)
    artistas_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Artista.objects.all(), required=False,
                                                      write_only=True)

    def create(self, validated_data):
        """
        Sobrecarga do método `create()` que realiza o seguinte procedimento

        1. verifica se os dados contêm "artistas_ids" (a lista de ids de artistas da música) e obtém seu valor, caso verdade
        2. acessa o "genero_id" dos dados, para que seja armazenado no campo "genero"
        3. cria a instância de "Musica" usando os dados, faz o clean e salva
        4. se houver dados de artistas, então define a lista de artistas e salva/atualiza os dados da música

        :param validated_data: Os dados de entrada
        :return: A música que foi cadastrada
        """
        artistas_data = None
        if 'artistas_ids' in validated_data:
            artistas_data = validated_data.pop('artistas_ids')

        genero_data = validated_data.pop('genero_id')

        musica = Musica(**validated_data)
        musica.genero = genero_data
        musica.full_clean()
        musica.save()

        if artistas_data:
            musica.artistas.set(artistas_data)
            musica.save()

        return musica

    def update(self, instance, validated_data):
        artistas_data = None
        if 'artistas_ids' in validated_data:
            artistas_data = validated_data.pop('artistas_ids')

        genero_data = None
        if 'genero_id' in validated_data:
            genero_data = validated_data.pop('genero_id')

        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.gostar = validated_data.get('gostar', instance.gostar)
        instance.naoGostar = validated_data.get('naoGostar', instance.naoGostar)
        instance.letra = validated_data.get('letra', instance.letra)
        instance.url_do_video = validated_data.get('url_do_video', instance.url_do_video)

        if genero_data:
            instance.genero = genero_data

        if artistas_data is not None:
            if len(artistas_data) > 0:
                instance.artistas.set(artistas_data)
            else:
                instance.artistas.clear()

        instance.full_clean()
        instance.save()

        return instance
