from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    """Тестируем модель Post из posts/models.py"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст'*10
        )

    def test_verbose_name_Post(self):
        """verbose_name в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_Post(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа поста',
            'image': 'Загрузите картинку',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_str_text_fild_Post(self):
        """В поле __str__  объекта post записано self.text[:15]."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    """Тестируем модель Group из posts/models.py"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовый текст описания'
        )
        cls.group = Group.objects.get(id=1)

    def test_verbose_name_Group(self):
        """verbose_name в полях Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_Group(self):
        """help_text в полях Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Сюда писать название группы',
            'description': 'Сюда писать описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_str_text_fild_Group(self):
        """В поле __str__  объекта group записано значение поля self.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
