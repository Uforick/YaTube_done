from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    }
)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.user2 = User.objects.create(username='testuser2')

        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='2',
            description='Тестовый текст описания'
        )

        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Тестовый текст'*10
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_slug', kwargs={
                'slug': PostURLTests.group.slug}),
            'posts/new.html': reverse('new_post'),
            'posts/post.html': reverse('post', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        """edit_post использует соответствующий шаблон."""
        template = 'posts/new.html'
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': PostURLTests.user.username,
            'post_id': PostURLTests.post.id,
        }),)
        self.assertTemplateUsed(response, template)

    def test_respone_for_gest_user(self):
        """Страницы '/', 'new/', 'group/<slug>',
        '/testuser/', '/testuser/1/', '/testuser/1/edit/'
        отвечают анонимному пользователю"""
        templates_url_names = {
            reverse('index'): 200,
            reverse('group_slug', kwargs={
                'slug': PostURLTests.group.slug}): 200,
            reverse('new_post'): 302,
            reverse('profile', kwargs={
                'username': PostURLTests.user.username}): 200,
            reverse('post', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }): 200,
            reverse('post_edit', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }): 302,

        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, template)

    def test_respone_for_author_user(self):
        """Страницы '/', 'new/', 'group/<slug>',
        '/testuser/', '/testuser/1/', '/testuser/1/edit/',
        'username>/<int:post_id>/comment'
        отвечают  авторизованному пользователю"""
        templates_url_names = {
            reverse('index'): 200,
            reverse('group_slug', kwargs={
                'slug': PostURLTests.group.slug}): 200,
            reverse('new_post'): 200,
            reverse('profile', kwargs={
                'username': PostURLTests.user.username}): 200,
            reverse('post', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }): 200,
            reverse('post_edit', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }): 200,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, template)

    def test_respone_edit_post_for_another_author(self):
        """Страница '/testuser/1/edit/'
        отвечает 302 не автору поста"""
        templates_url_names = {
            reverse('post_edit', kwargs={
                'username': PostURLTests.user.username,
                'post_id': PostURLTests.post.id,
            }): 302,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client2.get(url)
                self.assertEqual(response.status_code, template)

    def test_edit_redirect_anonymous_or_non_aythor(self):
        """Страница /edit/ перенаправит анонимного пользователя
        или не автора поста на сам пост.
        """
        user1 = self.guest_client
        user2 = self.authorized_client2
        url = reverse('post', kwargs={
            'username': PostURLTests.user.username,
            'post_id': PostURLTests.post.id,
        })
        templates_user = {
            user1: url,
            user2: url,
        }
        for user, url in templates_user.items():
            with self.subTest(url=url):
                response = user.get(reverse('post_edit', kwargs={
                    'username': PostURLTests.user.username,
                    'post_id': PostURLTests.post.id,
                }),
                    follow=True)
                self.assertRedirects(response, url)


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_404_custom_page(self):
        response = self.guest_client.get('/new/r/')
        self.assertEqual(response.status_code, 404)
