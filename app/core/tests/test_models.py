"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """"Test models."""

    def test_create_user_with_email_successsfull(self):
        """Tests creating a user with email is successfull."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(  # type: ignore
            email=email, password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_normalized_email(self):
        """Tests that the email of an user is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@example.COM', 'TEST3@example.com'],
            ['test4@EXAMPLE.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(  # type: ignore
                email, 'testsample123')
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        """Tests error if Try to create user with blank email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "hsfkjh3k")  # type: ignore

    def test_create_user_with_empty_email_raises_error(self):
        """Tests error if Try to create user with blank email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', "hsfkjh3k")  # type: ignore

    def test_create_superuser(self):
        """Test create super user"""
        user = get_user_model().objects.create_superuser(  # type: ignore
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
