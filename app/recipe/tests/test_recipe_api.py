"""Tests for Recipe API."""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPE_URL = reverse('recipe:recipe-list')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)  # type: ignore


def detail_url(recipe_id):
    """Create and return recipe detail url."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'SAmple Description',
        'link': 'http://example.com/recipe.pdf'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTest(TestCase):
    """Tests Unauthenticated requests for Recipe Api"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Tests if auth is required to call api"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Tests for Authenticated api requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@example.com',
                                password='testuserpass#1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_recipe_list_limited_to_user(self):
        """Test if a user can't view other user's recipes."""
        other_user = create_user(
            email='test2@example.com', password='test%pass$203')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_recipe_detail(self):
        """Test for recipe detail access."""

        recipe = create_recipe(user=self.user)

        res = self.client.get(detail_url(recipe.id))  # type: ignore
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_create_recipe(self):
        """Test for creating recipe."""
        payload = {
            'title': 'Sample Soup',
            'time_minutes': 30,
            'price': Decimal('23.96'),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])  # type: ignore
        for k, v in payload.items():  # type: ignore
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'http://example.com/'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe Title',
            link=original_link,
        )
        payload = {'title': 'New Recipe Title'}
        url = detail_url(recipe.id)  # type: ignore
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test for full update of recipe"""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe Title',
            link='http://link',
            description='sample description of a recipe',
            time_minutes=45,
            price=Decimal('345.89'),
        )

        payload = {
            'title': 'New Sample Recipe',
            'time_minutes': 22,
            'price': Decimal('5.25'),
            'description': 'SAmple Description',
            'link': 'http://example.com/recipe.pdf'
        }

        url = detail_url(recipe.id)  # type: ignore
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the user  of a recipe gives error"""
        new_user = create_user(email='teytsdf@example.com',
                               password='kladfioh5432skhcb')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user}

        url = detail_url(recipe.id)  # type: ignore
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test for delete recipe"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)  # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(
            id=recipe.id).exists())  # type: ignore

    def test_delete_other_user_recipe(self):
        """Test for a user can not delete other's recipe"""
        new_user = create_user(email='teytsdf@example.com',
                               password='kladfioh5432skhcb')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)  # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(
            id=recipe.id).exists())  # type: ignore
