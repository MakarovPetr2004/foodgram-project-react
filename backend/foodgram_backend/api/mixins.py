from rest_framework import status, permissions
from rest_framework.response import Response

from api.serializers import ShortenedRecipeReadSerializer


class AddToCollectionMixin:
    permission_classes = [permissions.IsAuthenticated]
    collection_model = None

    def add_to_collection(self, request, recipe):
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

    def remove_from_collection(self, request, recipe):
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
