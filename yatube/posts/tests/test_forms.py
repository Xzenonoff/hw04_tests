from http import HTTPStatus

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
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.form_data = {
            'text': cls.post.text,
            'group': cls.group.id
        }
        cls.reverses = {
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTests.post.id}
            ),
        }

    def setUp(self):
        self.quest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post_in_form(self):
        """Тест на создание поста в БД."""
        num_of_posts = Post.objects.count()
        self.authorized_user.post(
            self.reverses['post_create'],
            PostPagesTests.form_data
        )
        self.assertTrue(Post.objects.filter(
            author=PostPagesTests.user,
            text=PostPagesTests.post.text,
            group=PostPagesTests.group.id
        ).exists())
        new_post = Post.objects.last()
        pairs_for_test = [
            (Post.objects.count(), num_of_posts + 1),
            (new_post.text, PostPagesTests.post.text),
            (new_post.author, PostPagesTests.post.author),
            (new_post.group, PostPagesTests.post.group),
        ]
        for pair in pairs_for_test:
            with self.subTest(pair=pair):
                self.assertEqual(pair[0], pair[1])

    def test_edit_post_in_form(self):
        """Тест на проверку редактирования поста."""
        form_data_edit = {
            'text': 'Новый текст',
            'group': PostPagesTests.group.id
        }
        self.authorized_user.post(self.reverses['post_edit'], form_data_edit)
        response = self.authorized_user.get(self.reverses['post_edit'])
        self.assertEqual(response.context['post'].text, 'Новый текст')
        self.assertTrue(Post.objects.filter(
            text='Новый текст',
            group=PostPagesTests.group.id
        ).exists())

    def test_edit_and_create_post_quest(self):
        """
        Тест на проверку создания поста
        для незарегистрированного пользователя.
        """
        response = self.quest_client.post(
            self.reverses['post_create'], PostPagesTests.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_group_change(self):
        """Тест на проверку изменения группы поста."""
        group2 = Group.objects.create(
            title='Группа 2',
            slug='test-slug2'
        )
        form_data_edit = {
            'text': PostPagesTests.post.text,
            'group': group2.id,
            'id': PostPagesTests.post.id
        }
        self.authorized_user.post(
            self.reverses['post_edit'], form_data_edit
        )
        changed_post = Post.objects.get(id=PostPagesTests.post.id)
        self.assertEqual(changed_post.group.id, group2.id)
