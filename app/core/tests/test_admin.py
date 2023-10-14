"""Test admin site."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for admin site"""

    def setUp(self) -> None:
        """Create User and Clients."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(  # type: ignore
            "admin123@example.com", "tesTpass123")
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(  # type: ignore
            email="normaluser@example.com", name="User", password="user#125"
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Tests the user edit page"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        """Tests user add page."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertTrue(res.status_code, 200)
