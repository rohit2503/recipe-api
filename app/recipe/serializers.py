from rest_framework import serializers

from core.models import Tag, Ingredients, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Model Serializer class for Tag"""

    class Meta:
        model = Tag
        fields = ("id", "name",)
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Model Serializer class for Ingredient"""

    class Meta:
        model = Ingredients
        fields = ("id", "name",)
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer a recipe"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredients.objects.all())

    tag = serializers.PrimaryKeyRelatedField(many=True,
                                             queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tag', 'time_minutes',
                  'price', 'link')

        read_only = ('id', )


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)
