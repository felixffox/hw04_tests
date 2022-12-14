from django.contrib.auth import get_user_model
from posts.models import Group, Post
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test-user')
        cls.group = Group.objects.create(
            title='Test-title',
            slug='test-slug',
            description='Test-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test-text',
            group=cls.group
        )
        cls.form = PostCreateForm()

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test-text',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user.id,
                text='Test-text',
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        old_post = Post.objects.get(pk=self.post.id)
        another_group = Group.objects.create(
            title='Test-title-2',
            slug='test-slug-2'
        )
        form_data = {
            'text': 'Test-text',
            'group': another_group.pk,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.id, )),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        new_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(old_post.author, self.post.author)
        self.assertTrue(new_post.text == form_data['text'])
        self.assertTrue(new_post.group.pk == form_data['group'])
