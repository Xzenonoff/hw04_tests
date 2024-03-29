import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.form_data = {
            'text': 'тестовый текст',
            'group': cls.group.id,
        }
        cls.post_create_rev = reverse('posts:post_create')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(PostPagesTests.user)

    def test_create_post_in_form(self):
        """Тест на создание поста в БД."""
        num_of_posts = Post.objects.count()
        self.authorized_user.post(
            PostPagesTests.post_create_rev,
            PostPagesTests.form_data
        )
        self.assertTrue(Post.objects.filter(
            author=PostPagesTests.user,
            text='тестовый текст',
            group=PostPagesTests.group.id,
        ).exists())
        new_post = Post.objects.last()
        pairs_for_test = [
            (Post.objects.count(), num_of_posts + 1),
            (new_post.text, PostPagesTests.form_data['text']),
            (new_post.author, PostPagesTests.user),
            (new_post.group.id, PostPagesTests.form_data['group']),
        ]
        for response, expected in pairs_for_test:
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_edit_post_in_form_and_group_change(self):
        """Тест на проверку редактирования поста и изменения группы поста."""
        post = Post.objects.create(
            author=PostPagesTests.user,
            text='тестовый текст',
            group=PostPagesTests.group
        )
        post_edit_reverse = reverse(
            'posts:post_edit', kwargs={'post_id': post.id}
        )
        group2 = Group.objects.create(
            title='Группа 2',
            slug='test-slug2'
        )
        form_data_edit = {
            'text': 'Новый текст',
            'group': group2.id,
            'id': post.id
        }
        self.authorized_user.post(post_edit_reverse, form_data_edit)
        response = self.authorized_user.get(post_edit_reverse)
        self.assertEqual(response.context['post'].text, 'Новый текст')
        self.assertFalse(Post.objects.filter(
            text='Новый текст',
            group=PostPagesTests.group.id,
            id=post.id
        ).exists())
        self.assertTrue(Post.objects.filter(
            text='Новый текст',
            group=group2.id,
            id=post.id
        ).exists())

    def test_edit_and_create_post_guest(self):
        """
        Тест на проверку создания поста
        для незарегистрированного пользователя.
        """
        response = self.guest_client.post(
            PostPagesTests.post_create_rev, PostPagesTests.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/auth/login/?next=/create/')
