from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create sample recipe"""

    default_recipe = {"title": "Sample recipe",
                      "time_minutes": 10,
                      "price": 5.00
                      }

    default_recipe.update(params)

    return Recipe.objects.create(user=user, **default_recipe)


class PublicRecipeAPI(TestCase):
    """Test that Recipe need login"""

    def setUp(self):
        self.client = APIClient()

    def test_login_reqiuired_recipe_api(self):
        """Test that authorizatoion required for api access"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPI(TestCase):
    """Test that Recipe need login"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser_recipe@gmail.com", "passwprd_recipe")
        self.client.force_authenticate(self.user)

    def test_retreive_recipes(self):

        """Test retreiving recipe list"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test to limit the user specific recipes"""

        user = get_user_model().objects.create_user(
            "Another_recipe_user@another.com", "password123")

        sample_recipe(user=user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
