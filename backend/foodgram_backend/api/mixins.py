from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response

from api.serializers import ShortenedRecipeReadSerializer
from app import models


class AddToCollectionMixin:
    permission_classes = [permissions.IsAuthenticated]
    collection_model = None

    def post(self, request, id):
        recipe = get_object_or_404(models.Recipe, id=id)
        user = request.user
        collection, created = self.collection_model.objects.get_or_create(
            user=user, recipe=recipe
        )

        if created:
            serializer = ShortenedRecipeReadSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {'errors': 'Рецепт уже в коллекции'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        recipe = get_object_or_404(models.Recipe, id=id)

        user = request.user

        try:
            collection_recipe = self.collection_model.objects.get(
                user=user,
                recipe=recipe
            )
            collection_recipe.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.collection_model.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не находится в коллекции'},
                status=status.HTTP_400_BAD_REQUEST
            )
