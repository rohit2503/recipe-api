from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

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
    Test for authorized user for using API
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
