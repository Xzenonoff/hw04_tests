from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post

        group_expected = group.title
        post_str = post.text[:15]

        self.assertEqual(group_expected, group_expected.__str__())
        self.assertEqual(post_str, post.__str__())
