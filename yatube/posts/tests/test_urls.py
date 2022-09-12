from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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

    def test_urls_for_guest_client(self):
        templates_urls_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.post.author}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
        }
        for template, address in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_create_post_and_edit(self):
        addresses = [
            '/create/',
            f'/posts/{self.post.id}/edit/',
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

                response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_unexisting_page(self):
        response = self.guest_client.get('/random_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
