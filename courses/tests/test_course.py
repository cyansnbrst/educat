from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission

from courses.models import Subject, Course


class CourseViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        content_type = ContentType.objects.get_for_model(Course)
        view_permission = Permission.objects.get(
            content_type=content_type,
            codename='view_course'
        )
        add_permission = Permission.objects.get(
            content_type=content_type,
            codename='add_course'
        )
        change_permission = Permission.objects.get(
            content_type=content_type,
            codename='change_course'
        )
        delete_permission = Permission.objects.get(
            content_type=content_type,
            codename='delete_course'
        )
        self.user.user_permissions.add(view_permission, add_permission, change_permission, delete_permission)
        self.user.save()
        self.subject = Subject.objects.create(title='Test Subject')
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            overview='Test Overview',
            owner=self.user,
            subject=self.subject
        )
        self.list_url = reverse('manage_course_list')
        self.create_url = reverse('course_create')
        self.update_url = reverse('course_edit', args=[self.course.id])
        self.delete_url = reverse('course_delete', args=[self.course.id])

    def test_course_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')

    def test_course_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.create_url, {
            'title': 'New Course',
            'slug': 'new-course',
            'overview': 'New Overview',
            'subject': self.subject.id
        })
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_course_update_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.update_url, {
            'title': 'Updated Course',
            'slug': 'updated-course',
            'overview': 'Updated Overview',
            'subject': self.subject.id
        })
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')

    def test_course_delete_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.delete_url)
        self.assertFalse(Course.objects.filter(title='Test Course').exists())
