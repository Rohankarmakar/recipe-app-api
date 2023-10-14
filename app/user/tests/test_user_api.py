"""Tests for User Api."""
import email
from venv import create
from xml.dom import UserDataHandler
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)  # type: ignore


class PublicUserApiTest(TestCase):
    """Tests for Public User Api"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating  a user is successfull."""
        payload = {
            'email': 'test1@example.com',
            'password': 'test1234pass',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)  # type: ignore

    def test_user_not_created_with_existing_email(self):
        """Tests if user is not created with same email which already exists in the database."""

        payload = {
            'email': 'test@example.com',
            'password': 'test1234pass',
            'name': 'Test'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_not_created_with_short_password(self):
        """Tests if user is not created with short length password."""

        payload = {
            'email': 'test3@example.com',
            'password': 'test',
            'name': 'Test'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()

        self.assertFalse(user_exists)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Tests create token for users"""
        user_details = {
            'name': 'Test Name',
            'email': 'test123@example.com',
            'password': 'test-pass-123'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)  # type: ignore
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(email='test12@example.com', password='goodpass')

        payload = {
            'email': 'test12@example.com',
            'password': 'badpassword'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)  # type: ignore

    def test_create_token_blank_password(self):
        """Posting a blank password returns error"""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)  # type: ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test if unauthorized access to user is failed"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests for private user apis."""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@gmail.com',
            password='TestPas@123',
            name='Test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """Test if authenticated user can retrieve profile."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {  # type: ignore
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed_on_me(self):
        """Tests if POST method is not allowed on ME URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test if user profile is updatable."""
        payload = {
            'name': 'Updated Name',
            'password': 'UpdatedPass123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
