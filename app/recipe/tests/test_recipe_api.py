from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredients

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """:return recpe detail url"""

    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Main Course"):
    """ Create and return sample tag"""

    return Tag.objects.create(user=user, name=name)


def sample_ingredients(user, name="Cheese"):
    """Create and return ingredients object"""

    return Ingredients.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing detail page for recipe"""

        recipe = sample_recipe(self.user)
        recipe.tag.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredients(self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload = {"title": "Sample rceipe",
                   "time_minutes": 30,
                   "price": 10.00
                   }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.all()

        self.assertEqual(recipe.count(), 1)

        for keys in payload.keys():
            self.assertEqual(payload[keys], getattr(recipe[0], keys))

    def test_create_recipe_with_tags(self):
        """test to create the recipe with tags"""
        tag1 = sample_tag(self.user, name="lunch")
        tag2 = sample_tag(self.user, name="breakfast")

        payload = {"title": "Sample recipe",
                   "time_minutes": 30,
                   "price": 10.00,
                   "tag": [tag1.id, tag2.id]
                   }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tags = Tag.objects.all()

        self.assertEqual(tags.count(), 2)

        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_with_ingredients(self):
        """test recipe with ingredients"""

        ingr1 = sample_ingredients(self.user, name="Fish")
        ingr2 = sample_ingredients(self.user, name="Meat")

        payload = {"title": "Sample recipe",
                   "time_minutes": 30,
                   "price": 10.00,
                   "ingredients": [ingr1.id, ingr2.id]
                   }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredients = Ingredients.objects.all()

        self.assertEqual(ingredients.count(), 2)

        self.assertIn(ingr1, ingredients)
        self.assertIn(ingr2, ingredients)
