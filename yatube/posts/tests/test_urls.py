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

    def test_urls_for_guest_and_auth_client(self):
        templates_urls_names = {
            'posts/index.html': ('/', HTTPStatus.OK, HTTPStatus.OK),
            'posts/group_list.html': (
                f'/group/{StaticURLTests.group.slug}/',
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            'posts/profile.html': (
                f'/profile/{StaticURLTests.post.author}/',
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            'posts/post_detail.html': (
                f'/posts/{StaticURLTests.post.id}/',
                HTTPStatus.OK,
                HTTPStatus.OK
            ),
            'posts/create_post.html': (
                '/create/', HTTPStatus.FOUND, HTTPStatus.OK
            ),
        }
        for template, address_codes in templates_urls_names.items():
            with self.subTest(address=address_codes):
                response_quest = self.guest_client.get(address_codes[0])
                self.assertEqual(response_quest.status_code, address_codes[1])

                response_auth = self.authorized_user.get(address_codes[0])
                self.assertEqual(response_auth.status_code, address_codes[2])

    def test_urls_create_post_and_edit(self):
        addresses = [
            '/create/',
            f'/posts/{StaticURLTests.post.id}/edit/',
        ]
        for address in addresses:
            with self.subTest(address=address):
                response_quest = self.guest_client.get(address)
                self.assertEqual(response_quest.status_code, HTTPStatus.FOUND)
                self.assertRedirects(
                    response_quest,
                    f'/auth/login/?next={address}'
                )

                response_auth = self.authorized_user.get(address)
                self.assertEqual(response_auth.status_code, HTTPStatus.OK)

    def test_urls_unexisting_page(self):
        response = self.guest_client.get('/random_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
