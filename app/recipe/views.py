from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredients, Recipe
from recipe import serializers


class BaseRecipeAttr(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """:return objects for current user authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSets(BaseRecipeAttr):
    """ Manage tags in database"""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSets(BaseRecipeAttr):

    """ Manage ingredients in database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredients.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def _parse_string_to_int(self, qs):
        """convert list of string to list of int"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the recipe for authentocated users"""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            tag_ids = self._parse_string_to_int(tags)
            queryset = queryset.filter(tag__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._parse_string_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerialzer

        return self.serializer_class

    def perform_create(self, serializer):
        """perform create of object"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uplaod an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
