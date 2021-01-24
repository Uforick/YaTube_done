import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа 3',
            slug='3',
            description='Тестовый текст описания'
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Тестовый текст'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_title_label(self):
        """labels совпадает с ожидаемым."""
        title_label = PostCreateFormTests.form
        field_labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_labels.items():
            with self.subTest(value=value):
                self.assertEqual(
                    title_label.fields[value].label, expected)

    def test_title_help_text(self):
        """help_text совпадает с ожидаемым."""
        title_help_text = PostCreateFormTests.form
        field_help_text = {
            'text': 'Текст поста',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    title_help_text.fields[value].help_text, expected)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        form_data = {
            'text': 'Другой тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': PostCreateFormTests.post.id
            }),
            data=form_data,
            follow=True
        )
        edit_text = Post.objects.get(id=1).text
        self.assertRedirects(response, reverse('post', kwargs={
            'username': self.user.username,
            'post_id': PostCreateFormTests.post.id
        }))
        self.assertEqual(
            edit_text,
            form_data['text'])
