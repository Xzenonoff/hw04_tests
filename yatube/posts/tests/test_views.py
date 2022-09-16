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
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            pub_date='02.09.2022'
        )
        cls.reverses = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': PostPagesTests.group.slug}
            ),
            'profile': reverse('posts:profile', kwargs={
                'username': PostPagesTests.post.author.username
            }),
            'post_detail': reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTests.post.id}
            ),
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTests.post.id}
            ),
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def context_post_assert(self, obj):
        self.assertEqual(obj.text, PostPagesTests.post.text)
        self.assertEqual(obj.group, PostPagesTests.post.group)
        self.assertEqual(obj.author, PostPagesTests.post.author)
        self.assertEqual(obj.pub_date, PostPagesTests.post.pub_date)

    def test_pages_uses_correct_template(self):
        """URL использует соответствующий шаблон."""
        templates = (
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        )
        for reverse_name, template in zip(self.reverses.values(), templates):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_has_correct_context(self):
        """Тест контекста для index, group_list, profile."""
        keys = ('index', 'group_list', 'profile')
        for key in keys:
            with self.subTest(key=key):
                response = self.authorized_user.get(self.reverses[key])
                self.context_post_assert(response.context['page_obj'][0])

    def test_post_detail_has_correct_context(self):
        """Тест контекста для detail."""
        response = self.authorized_user.get(self.reverses['post_detail'])
        self.context_post_assert(response.context['post'])
        self.assertEqual(
            response.context['post'].author.posts.count(),
            PostPagesTests.post.author.posts.count()
        )

    def test_create_post_has_correct_context(self):
        """Тест контекста для create."""
        response = self.authorized_user.get(self.reverses['post_create'])
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_has_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_user.get(self.reverses['post_edit'])
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)

    def test_post_create_group_check(self):
        """Тест добавления поста при указании группы."""
        pages = (
            self.reverses['index'],
            self.reverses['group_list'],
            self.reverses['profile'],
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_user.get(page)
                self.assertEqual(
                    response.context.get('page_obj')[0],
                    PostPagesTests.post,
                    f'{PostPagesTests.post.id}'
                )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        objs = (Post(
            text=f'{i} тестовый текст',
            author=cls.user,
            group=cls.group
        ) for i in range(14))
        cls.post = Post.objects.bulk_create(objs)

    def test_paginator(self):
        """Проверяем, что Paginator работает корректно."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.user.username
            }),
        )
        page_posts = [
            ({'page': 1}, 10),
            ({'page': 2}, 4),
        ]
        for page, page_post in zip(pages, page_posts):
            with self.subTest(page=page):
                response = self.authorized_user.get(page, page_post[0])
                self.assertEqual(
                    len(response.context['page_obj']), page_post[1]
                )
