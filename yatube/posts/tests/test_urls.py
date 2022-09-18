from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


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
        cls.public_addresses = [
            ('posts/index.html', '/'),
            ('posts/group_list.html', f'/group/{StaticURLTests.group.slug}/'),
            ('posts/profile.html', f'/profile/{StaticURLTests.post.author}/'),
            ('posts/post_detail.html', f'/posts/{StaticURLTests.post.id}/'),
        ]
        cls.private_addresses = [
            ('posts/create_post.html', '/create/'),
            (
                'posts/create_post.html',
                f'/posts/{StaticURLTests.post.id}/edit/'
            ),
        ]

    def test_urls_for_guest_client(self):
        """Тест URL для неавторизованного пользователя."""
        for template, address in self.public_addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for template, address in self.private_addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_for_auth_client(self):
        """Тест URL для авторизованного пользователя."""
        for template, address in self.public_addresses:
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for template, address in self.private_addresses:
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

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
