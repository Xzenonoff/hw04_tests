from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group',)
        labels = {
            'text': 'Текст',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Укажите группу поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }
