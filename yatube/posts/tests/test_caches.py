from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class CachesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
        )

    def setUp(self):
        self.client = Client()

    def test_index_cache(self):
        """Проверка кэширования страницы index."""
        response = self.client.get(reverse('posts:index'))
        self.assertIn(
            CachesTests.post.text, response.context['page_obj'][0].text
        )
        temp = response.content
        Post.objects.get(id=CachesTests.post.id).delete()
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(len(temp), len(response_2.content))
        cache.clear()
        response_3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(len(temp), len(response_3.content))
