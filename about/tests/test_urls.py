from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_respone_for_gest_user(self):
        """Страницы '/about/author/', и '/about/tech/'
        отвечают анонимному пользователю"""
        templates_url_names = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, template)

        def test_urls_uses_correct_template(self):
            """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
