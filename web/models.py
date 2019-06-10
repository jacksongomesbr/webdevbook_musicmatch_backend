from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class ArtistaManager(models.Manager):
    def is_valid(self, artista):
        if artista.url_da_foto and artista.url_da_foto.startswith('https'):
            raise ValidationError({
                'url_da_foto': 'A URL da foto não pode usar o protocolo HTTPS'
            })


class Artista(models.Model):
    nome = models.CharField(max_length=64)
    foto = models.ImageField(null=True, blank=True, upload_to='fotos/%Y/%m/%d/')
    url_da_foto = models.URLField(null=True, blank=True)
    objects = ArtistaManager()

    def clean(self):
        # self.objects.is_valid(self)
        if self.url_da_foto and self.url_da_foto.startswith('https'):
            raise ValidationError({
                'url_da_foto': 'A URL da foto não pode usar o protocolo HTTPS'
            })

    def __str__(self):
        return self.nome


class Genero(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.nome


class Musica(models.Model):
    titulo = models.CharField(max_length=128)
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE, related_name='musicas')
    gostar = models.IntegerField(default=0)
    naoGostar = models.IntegerField(default=0)
    letra = models.TextField(null=True, blank=True)
    artistas = models.ManyToManyField(Artista, related_name='musicas', blank=True)
    url_do_video = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.titulo
