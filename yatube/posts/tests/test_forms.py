from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post_in_form(self):
        """Тест на создание поста в БД."""
        num_of_posts = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост из формы',
            'group': self.group.id
        }
        self.authorized_user.post(reverse('posts:post_create'), data=form_data)
        self.assertEqual(Post.objects.count(), num_of_posts + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый пост из формы',
            group=self.group.id
        ).exists())

    def test_edit_post_in_form(self):
        """Тест на проверку редактирования поста."""
        form_data = {
            'text': 'Новый текст',
            'group': self.group.id
        }
        self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        response = self.authorized_user.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'].text, 'Новый текст')
        self.assertTrue(Post.objects.filter(
            text='Новый текст',
            group=self.group.id
        ).exists())
