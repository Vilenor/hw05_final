import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post_id=cls.post.id
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_id_0 = first_object.id
        post_image_0 = first_object.image

        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_author_0, PostPagesTests.post.author.username)
        self.assertEqual(post_group_0, PostPagesTests.group.title)
        self.assertEqual(post_id_0, PostPagesTests.post.id)
        self.assertEqual(post_image_0, PostPagesTests.post.image)
        self.assertIn('page_obj', response.context)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                ('posts:group_list'),
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        group_title_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, PostPagesTests.post.image)
        self.assertEqual(group_description_0, PostPagesTests.group.description)
        self.assertEqual(group_slug_0, PostPagesTests.group.slug)
        self.assertEqual(group_title_0, PostPagesTests.group.title)
        self.assertIn('group', response.context)
        self.assertIn('page_obj', response.context)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                ('posts:profile'),
                kwargs={'username': PostPagesTests.post.author.username}
            )
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, PostPagesTests.post.image)
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(
            response.context['author'].username,
            PostPagesTests.post.author.username
        )
        self.assertEqual(
            response.context['count_posts'],
            PostPagesTests.post.author.posts.count()
        )
        self.assertIn('author', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIn('count_posts', response.context)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                ('posts:post_detail'),
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        self.assertEqual(
            response.context['post'].image,
            PostPagesTests.post.image
        )
        self.assertEqual(
            response.context['post'].text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            response.context['count_posts'],
            PostPagesTests.post.author.posts.count()
        )
        self.assertIn('post', response.context)
        self.assertIn('count_posts', response.context)
        self.assertIn('comments', response.context)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertIn('form', response.context)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertIn('form', response.context)
        self.assertIn('is_edit', response.context)
        self.assertEqual(response.context['is_edit'], True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post_list = [
            Post(
                text='Текст',
                author=cls.user,
                group=cls.group
            ) for i in range(13)
        ]
        cls.post = Post.objects.bulk_create(post_list)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsernameFollower')
        cls.author = User.objects.create_user(username='TestUsernameAuthor')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewsTest.user)

    def test_user_following_list(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            self.post,
            response.context['page_obj']
        )
        # Проверяем что новая запись появляется в ленте у подписанного
        new_post = Post.objects.create(
            text='Второй пост',
            author=FollowViewsTest.author
        )
        response_2 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            new_post,
            response_2.context['page_obj']
        )

    def test_user_unfollowing_list(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context['page_obj'])
        # Проверяем что новая запись НЕ появляется в ленте у не подписанного
        new_post = Post.objects.create(
            text='Второй пост',
            author=FollowViewsTest.author
        )
        response_2 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            new_post,
            response_2.context['page_obj']
        )
