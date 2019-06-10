from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Artista, Musica


class WebApiTests(APITestCase):
    fixtures = ['artistas.json', 'generos.json', 'musicas.json']

    def test_cont_artistas_igual_2(self):
        self.assertEqual(Artista.objects.count(), 2)

    def test_create_artista(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('web:artistas-list')
        data = {'nome': 'Martinho Da Vila'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artista.objects.count(), 3)
        self.assertEqual(response.data['id'], 3)
        self.assertEqual(Artista.objects.get(nome='Martinho Da Vila').nome, 'Martinho Da Vila')

    def test_list_artistas(self):
        url = reverse('web:artistas-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # self.assertEqual(Artista.objects.count(), 1)

    def test_detail_artista_existente(self):
        url = reverse('web:artistas-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['nome'], 'Beth Carvalho')

    def test_detail_artista_nao_existente(self):
        url = reverse('web:artistas-detail', kwargs={'pk': 5})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_artista(self):
        url = reverse('web:artistas-detail', kwargs={'pk': 1})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cont_musicas_igual_2(self):
        self.assertEqual(Musica.objects.count(), 2)
