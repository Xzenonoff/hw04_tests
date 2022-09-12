from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.guest_client = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        """URL использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_has_correct_context(self):
        """Тест контекста для index."""
        response = self.authorized_user.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)

    def test_group_list_has_correct_context(self):
        """Тест контекста для group_list."""
        response = self.authorized_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)

    def test_profile_has_correct_context(self):
        """Тест контекста для profile."""
        response = self.authorized_user.get(
            reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)

    def test_post_detail_has_correct_context(self):
        """Тест контекста для detail."""
        response = self.authorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(
            first_object.author.posts.count(),
            self.post.author.posts.count()
        )

    def test_create_post_has_correct_context(self):
        """Тест контекста для create."""
        response = self.authorized_user.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_has_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_user.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)

    def test_post_create_group_check(self):
        """Тест добавления поста при указании группы."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_user.get(page)
                self.assertEqual(
                    response.context.get('page_obj')[0],
                    self.post,
                    f'{self.post.id}'
                )
