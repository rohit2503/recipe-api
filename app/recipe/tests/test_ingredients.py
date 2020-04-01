from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients

from recipe.serializers import IngredientSerializer


INGREDIENTS_URLS = reverse("recipe:ingredients-list")


class PublicIngredientsTests(TestCase):
    """Test case for Public Incredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that require ingredients API"""

        res = self.client.get(INGREDIENTS_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsTests(TestCase):
    """Test case that for Private Ingredients """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_ingredient@gmail.com",
            password="test_password")
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieve a list of ingredients"""

        Ingredients.objects.create(user=self.user, name="coconut")
        Ingredients.objects.create(user=self.user, name="cucumber")

        res = self.client.get(INGREDIENTS_URLS)

        ingredients = Ingredients.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test to verify the ingredients limited to user"""

        user = get_user_model().objects.create_user(
            "Anothertestuser@gmail.com",
            "password")

        Ingredients.objects.create(user=user, name="vingegar")

        ing = Ingredients.objects.create(user=self.user, name="flour")

        res = self.client.get(INGREDIENTS_URLS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ing.name)

    def create_successful_ingredient(self):
        """
        Test Create new ingredient
        """
        payload = {"name": "Flour"}
        self.client.post(INGREDIENTS_URLS, payload)

        exists = Ingredients.objects.filter(name=payload["name"],
                                            user=self.user).exists()
        self.assertTrue(exists)

    def create_invalid_ingredients(self):
        """Test for invalid ingredients"""
        payload = {"name": ""}

        res = self.client.post(INGREDIENTS_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
