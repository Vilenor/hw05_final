from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostsURLTests.user,
        )

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestUsername/': 'posts/profile.html',
            f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/404/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_uses_correct_template(self):
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/',
            context={'is_edit': True}
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    # Проверяем доступность страниц для любого пользователя
    def test_homepage(self):
        """Стартовая страница доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/TestUsername/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/TestUsername/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_id_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{PostsURLTests.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Страница /unexisting/ вызывает ошибку 404."""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_exists_at_desired_location_authorized(self):
        """Страница /posts/<int:post_id>/edit/
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_url_redirect_anonymous(self):
        """Страница /posts/<int:post_id>/edit/
        перенаправляет анонимного пользователя.
        """
        response = self.guest_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_post_url_redirect_anonymous(self):
        """Страница /posts/<int:post_id>/comment/
        перенаправляет анонимного пользователя.
        """
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.id}/comment/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
