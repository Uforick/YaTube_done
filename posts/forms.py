from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
            'image': ('Картинка'),
        }
        help_texts = {
            'text': ('Текст поста'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': ('Текст'),
        }
        help_texts = {
            'text': ('Текст комментария'),
        }
