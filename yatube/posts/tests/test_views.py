from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст',
            group=cls.group,
            pub_date='02.09.2022'
        )
        cls.reverses = {
            'index': ('posts/index.html', reverse('posts:index')),
            'group_list': (
                'posts/group_list.html', reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group.slug}
                )
            ),
            'profile': (
                'posts/profile.html', reverse(
                    'posts:profile',
                    kwargs={'username': cls.post.author.username}
                )
            ),
            'post_detail': (
                'posts/post_detail.html', reverse(
                    'posts:post_detail',
                    kwargs={'post_id': cls.post.id}
                )
            ),
            'post_create': (
                'posts/create_post.html', reverse('posts:post_create')
            ),
            'post_edit': (
                'posts/create_post.html', reverse(
                    'posts:post_edit',
                    kwargs={'post_id': cls.post.id}
                )
            )
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            ),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def context_post_assert(self, obj):
        self.assertEqual(obj.text, PostPagesTests.post.text)
        self.assertEqual(obj.group, PostPagesTests.post.group)
        self.assertEqual(obj.author, PostPagesTests.post.author)
        self.assertEqual(obj.pub_date, PostPagesTests.post.pub_date)

    def test_pages_uses_correct_template(self):
        """URL использует соответствующий шаблон."""
        for template, reverse_name in self.reverses.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_has_correct_context(self):
        """Тест контекста для index, group_list, profile."""
        for url in PostPagesTests.urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.context_post_assert(response.context['page_obj'][0])

    def test_post_detail_has_correct_context(self):
        """Тест контекста для detail."""
        response = self.authorized_user.get(self.reverses['post_detail'][1])
        self.context_post_assert(response.context['post'])
        self.assertEqual(
            response.context['post'].author.posts.count(),
            PostPagesTests.post.author.posts.count()
        )

    def test_create_post_has_correct_context(self):
        """Тест контекста для create."""
        response = self.authorized_user.get(self.reverses['post_create'][1])
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_has_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_user.get(self.reverses['post_edit'][1])
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)

    def test_post_create_group_check(self):
        """Тест добавления поста при указании группы."""
        for url in PostPagesTests.urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertEqual(
                    response.context.get('page_obj')[0],
                    PostPagesTests.post,
                    f'{PostPagesTests.post.id}'
                )

    def test_paginator(self):
        """Проверяем, что Paginator работает корректно."""
        objs = [
            Post(
                text=f'текст {i}',
                author=PostPagesTests.user,
                group=PostPagesTests.group,
            ) for i in range(13)
        ]
        Post.objects.bulk_create(objs)
        page_posts = [
            (1, 10),
            (2, 4),
        ]
        for url in PostPagesTests.urls:
            with self.subTest(url=url):
                for page, post_num in page_posts:
                    response = self.authorized_user.get(url, {'page': page})
                    self.assertEqual(
                        len(response.context['page_obj']), post_num
                    )
