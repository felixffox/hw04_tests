from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()

TESTS_POSTS_NUM = 13


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Test-group',
            slug='test-slug',
            description='Test-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test-post',
            pk='30',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'HasNoName'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': '30'}),
            'posts:post_create': reverse(
                'posts/create_post.html'),
            'posts:post_edit': reverse(
                'posts/create_post.html',
                kwargs={'post_id': '30'}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_text_0, 'Test-post')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Test-group')

    def test_group_list_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        post_object = response.context['page_obj'][0]
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_text_0, 'Test-post')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Test-group')

    def test_profile_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        post_object = response.context['page_obj'][0]
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_text_0, 'Test-post')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Test-group')

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '30'}))
        post_object = response.context['post']
        post_text_0 = post_object.text
        post_author_0 = post_object.author.username
        post_group_0 = post_object.group.title
        self.assertEqual(post_text_0, 'Test-post')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Test-group')

    def test_post_create_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '30'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Test-title',
            slug='test-slug',
            description='Test-description',
        )
        cls.post = []
        for i in range(TESTS_POSTS_NUM):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    text=f'Test-text {i}',
                    group=cls.group,
                )
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page(self):
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page(self):
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_new_post(self):
        post_0 = Post.objects.create(
            author=User.objects.create_user(username='Test-User'),
            text='Test-text',
            group=Group.objects.last()
        )
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Test-User'}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                posts = response.context['page_obj'].object_list

                posts_ids = []
                for post in posts:
                    posts_ids.append(post.id)
                self.assertIn(post_0.id, posts_ids)
