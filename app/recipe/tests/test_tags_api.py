from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    """
    Test the publicly available tag API
    """

    def setUp(self):

        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for accessing tags
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Tests for authorized user for using API
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_tags(self):
        """Test for retrieving tha tags"""

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="NonVegan")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test that tags returned for authenticated user"""

        user = get_user_model().objects.create_user(email="testuser12",
                                                    password="password121")

        Tag.objects.create(user=user, name="Fruity")

        tag = Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_success(self):
        """
         Test to create the tag with valid payload
        """

        payload = {"name": "Spicy"}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Tag.objects.filter(user=self.user,
                                    name=payload["name"]).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating new tag with invalid payload"""

        payload = {"name": ""}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tags_assigned_to_recipe(self):
        """Test filtering tags bu those assigned to recipes"""

        tags1 = Tag.objects.create(user=self.user, name="Breakfast")
        tags2 = Tag.objects.create(user=self.user, name="Lunch")

        recipe1 = Recipe.objects.create(
            title="Coriander eggs",
            time_minutes=2,
            price=5.00,
            user=self.user
        )

        recipe1.tag.add(tags1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tags1)
        serializer2 = TagSerializer(tags2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            title="Pancake",
            time_minutes=30,
            price=23.00,
            user=self.user
        )
        recipe1.tag.add(tag)

        recipe2 = Recipe.objects.create(
            title="Cakes",
            time_minutes=30,
            price=23.00,
            user=self.user
        )

        recipe2.tag.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
