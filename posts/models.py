from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        help_text='Сюда писать название группы',
        max_length=200
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Сюда писать описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста'
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True,
        help_text='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='posts',
        blank=True,
        null=True,
        help_text='Группа поста'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
        help_text='Комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Автор комментария к посту'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст комментария'
    )
    created = models.DateTimeField(
        'date published',
        auto_now_add=True,
        help_text='Дата размещения'
    )

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Кто подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text='На кого подписываются'
    )
