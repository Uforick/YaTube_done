import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Follow

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    MEDIA_ROOT=MEDIA_ROOT,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        }
    }
)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.user2 = User.objects.create(username='testuser2')
        cls.group = Group.objects.create(
            id=1,
            title='Тестовая группа 3',
            slug='3',
            description='Тестовый текст описания'
        )
        cls.group2 = Group.objects.create(
            id=2,
            title='Тестовая группа 4',
            slug='4',
            description='Тестовый текст описания2'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for num in range(12):
            Post.objects.create(
                id=num,
                group=cls.group,
                author=cls.user,
                text='Тестовый текст',
                image=uploaded
            )
        cls.post = Post.objects.get(id=1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'posts/new.html': reverse('new_post'),
            'group.html': (
                reverse(
                    'group_slug', kwargs={'slug': ViewsTests.group.slug})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_all_contexte_correct(self):
        """Шаблоны index, group и username с правильным контекстом."""
        index_response = self.guest_client.get(reverse('index'))
        group_response = self.guest_client.get(
            reverse('group_slug', kwargs={'slug': ViewsTests.group.slug})
        )
        username_response = self.guest_client.get(
            reverse('profile', kwargs={'username': ViewsTests.user.username})
        )
        all_context = [index_response, group_response, username_response]
        value_context = 'page'
        self.check_correct_context(value_context, all_context)

    def test_username_post_id_show_correct_context(self):
        """Шаблон username_post_id сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': ViewsTests.user.username,
                'post_id': ViewsTests.post.id
            }))
        value_context = 'post'
        self.check_correct_context(value_context, response)

    def check_correct_context(self, value_context, context_dic):
        if value_context == 'page':
            for num in context_dic:
                post_group = num.context.get('page')[0].group
                post_author = num.context.get('page')[0].author
                post_text = num.context.get('page')[0].text
                post_image = num.context.get('page')[0].image
        elif value_context == 'post':
            post_group = context_dic.context.get('post').group
            post_author = context_dic.context.get('post').author
            post_text = context_dic.context.get('post').text
            post_image = context_dic.context.get('post').image
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertIsNotNone(post_image)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': ViewsTests.user.username,
            'post_id': ViewsTests.post.id
        }))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_main_page_list_is_10(self):
        """На главной странице есть 10 из 12 записей"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 10)

    def test_group_page_list_is_10(self):
        """На странице группы1 есть 10 из 12 записей"""
        response = self.authorized_client.get(
            reverse('group_slug', kwargs={'slug': ViewsTests.group.slug})
        )
        self.assertEqual(len(response.context['page']), 10)

    def test_group_page_list_is_1(self):
        """На странице группы2 нет записи"""
        response = self.authorized_client.get(
            reverse('group_slug', kwargs={'slug': ViewsTests.group2.slug})
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_login_user_can_follow_unfollow(self):
        """Авторизованный пользователь может подписываться
        и удалять из подписок."""
        follow_count = 0
        follower = self.authorized_client2
        name = ViewsTests.user2
        follower.post(
            reverse('profile_follow', kwargs={
                    'username': ViewsTests.post.author})
        )
        follow_count = Follow.objects.filter(user=name).count()
        self.assertEqual(follow_count, 1)
        follower.post(
            reverse('profile_unfollow', kwargs={
                    'username': ViewsTests.post.author})
        )
        follow_count = Follow.objects.filter(user=name).count()
        self.assertEqual(follow_count, 0)

    def test_follow_unfollow_post(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него"""
        Follow.objects.create(
            user=ViewsTests.user,
            author=ViewsTests.user2,
        )
        response1 = self.authorized_client.get(
            reverse('follow_index')
        )
        response2 = self.authorized_client2.get(
            reverse('follow_index')
        )
        self.assertEqual(len(response1.context['page']), 0)
        self.assertEqual(len(response2.context['page']), 0)
        form_data = {
            'text': 'Тестовый текст',
        }
        self.authorized_client2.post(
            reverse('new_post'),
            data=form_data,
            follow=False
        )
        response1 = self.authorized_client.get(
            reverse('follow_index')
        )
        response2 = self.authorized_client2.get(
            reverse('follow_index')
        )
        self.assertEqual(len(response1.context['page']), 1)
        self.assertEqual(len(response2.context['page']), 0)

    def test_add_comment_for_user(self):
        """Только авторизированный пользователь может комментировать посты"""
        form_data = {
            'text': 'Тестовый текст',
        }
        self.guest_client.post(
            reverse('add_comment', kwargs={
                    'username': ViewsTests.post.author,
                    'post_id': ViewsTests.post.id
                    }),
            data=form_data
        )
        response = self.authorized_client.get(
            reverse('post', kwargs={
                    'username': ViewsTests.post.author,
                    'post_id': ViewsTests.post.id
                    }))
        self.assertEqual(len(response.context['comments']), 0)
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                    'username': ViewsTests.post.author,
                    'post_id': ViewsTests.post.id
                    }),
            data=form_data
        )
        response = self.authorized_client.get(
            reverse('post', kwargs={
                    'username': ViewsTests.post.author,
                    'post_id': ViewsTests.post.id
                    }))
        self.assertEqual(len(response.context['comments']), 1)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')

        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый текст'*10
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_chache_index_page(self):
        """Тест: новый пост не появляется на главной странице"""
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                    'username': CacheTests.post.author,
                    'post_id': CacheTests.post.id
                    }),
            data=form_data
        )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)
