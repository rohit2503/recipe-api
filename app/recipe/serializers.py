from rest_framework import serializers

from core.models import Tag, Ingredients


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
