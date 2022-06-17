from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post_id=cls.post.id
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_models_Post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_models_Group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_Comment_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        comment = PostModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

    def test_models_Follow_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        follow = PostModelTest.follow
        expected_object_name = str(follow.author)
        self.assertEqual(expected_object_name, str(follow))
