from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_sample_users(email="testsampleuser@gmail.com",
                        password="password2020"):

    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """
    Test cases to test customized User model
    """

    def test_create_user_with_email(self):
        """
        Test creating with user email successful
        :return:
        """
        email = 'abc@xyz.com'
        password = 'Test123'

        user = get_user_model().objects.create_user(email=email,
                                                    password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalization(self):
        """
        Test to check the user email normalization
        :return:
        """
        email = 'abc@XYZ.COM'

        user = get_user_model().objects.create_user(email=email,
                                                    password='test123')

        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        """
        Test user email validation
        :return:
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None,
                                                 password='test123')

    def test_user_create_superuser(self):
        """
        Test create super user
        :return:
        """
        email = 'testsuperuser@xyz.com'
        user = get_user_model().objects.create_superuser(email=email,
                                                         password='super123')
        self.assertTrue(user.is_superuser, email)
        self.assertTrue(user.is_staff, email)

    def test_tag_str(self):
        """
        sample test to tag string representation
        """

        tag = models.Tag.objects.create(user=create_sample_users(),
                                        name='Vegan')

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """
        sample test to ingredients string representation
        """

        ingredients = models.Ingredients.objects.create(
            user=create_sample_users(),
            name='Coconut')

        self.assertEqual(str(ingredients), ingredients.name)


    def test_recipe_str(self):
        """
        sample test to recipe string representation
        """

        recipe = models.Recipe.objects.create(
            user=create_sample_users(),
            name='Coconut')

        self.assertEqual(str(recipe), recipe.name)
