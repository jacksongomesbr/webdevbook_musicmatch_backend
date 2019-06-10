from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from .models import *


class ArtistaResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'nome': 'title',
        'urlDaFoto': 'url_da_foto'
    })

    # GET /api/posts/ (but not hooked up yet)
    def list(self):
        return Artista.objects.all()

    # GET /api/posts/<pk>/ (but not hooked up yet)
    def detail(self, pk):
        return Artista.objects.get(id=pk)