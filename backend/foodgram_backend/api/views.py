from collections import defaultdict

from api import serializers
from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from app.models import (FavoriteRecipe, FollowAuthor, Ingredient, Recipe,
                        RecipeIngredient, ShoppingCartRecipe, Tag)
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class NewUserViewSet(UserViewSet):
    http_method_names = ['get', 'post']

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        subscribed_users = User.objects.filter(following__user=user)

        page = self.paginate_queryset(subscribed_users)
        serializer = serializers.UserRecipeSerializer(
            page, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        term = self.request.query_params.get('name', '').strip()

        if term:
            queryset = queryset.filter(
                Q(name__istartswith=term) | Q(name__icontains=term)
            )
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeReadSerializer
        return serializers.RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if not user.is_authenticated:
            return queryset

        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if is_favorited not in ('0', '1') and is_favorited:
            raise ValidationError("is_favorited должен быть '0' или '1'.")
        if is_in_shopping_cart not in ('0', '1') and is_in_shopping_cart:
            raise ValidationError(
                "is_in_shopping_cart должен быть '0' или '1'."
            )

        queryset = queryset.annotate(
            num_favorites=Count(
                'favorited_by',
                filter=Q(favorited_by__user=user)
            ),
            num_cart=Count(
                'added_to_cart_by',
                filter=Q(added_to_cart_by__user=user)
            )
        )

        if is_favorited == '1':
            queryset = queryset.filter(num_favorites__gt=0)
        elif is_favorited == '0':
            queryset = queryset.filter(num_favorites=0)

        if is_in_shopping_cart == '1':
            queryset = queryset.filter(num_cart__gt=0)
        elif is_in_shopping_cart == '0':
            queryset = queryset.filter(num_cart=0)

        return queryset

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        cart_recipes = ShoppingCartRecipe.objects.filter(user=user)

        if cart_recipes:
            shopping_list = defaultdict(dict)

            for cart_recipe in cart_recipes:
                recipe_ingredients = RecipeIngredient.objects.filter(
                    recipe=cart_recipe.recipe)
                for ingredient in recipe_ingredients:
                    ingredient_name = ingredient.ingredient.name
                    amount = ingredient.amount
                    measurement_unit = ingredient.ingredient.measurement_unit

                    if ingredient_name in shopping_list:
                        shopping_list[ingredient_name]['amount'] += amount
                    else:
                        shopping_list[ingredient_name] = {
                            'amount': amount,
                            'measurement_unit': measurement_unit
                        }

            response = HttpResponse(content_type='text/plain')
            response[
                'Content-Disposition'
            ] = 'attachment; filename="shopping_list.txt"'

            response.write('Список покупок:\n\n')
            for ingredient_name, info in shopping_list.items():
                amount = info['amount']
                measurement_unit = info['measurement_unit']
                response.write(
                    f'{ingredient_name} — {amount}'
                    f' {measurement_unit}\n'
                )

            return response

        return HttpResponse(
            'У вас нет рецептов в корзине',
            content_type='text/plain',
            status=status.HTTP_404_NOT_FOUND
        )


class FollowAuthorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        user = request.user

        following_user = get_object_or_404(User, id=id)

        if user == following_user:
            return Response({
                'errors': 'Нельзя подписаться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow, created = FollowAuthor.objects.get_or_create(
            user=user, following=following_user
        )

        if created:
            serializer = serializers.UserRecipeSerializer(
                following_user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'errors': 'Вы уже подписаны на этого автора'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = request.user

        following = get_object_or_404(User, id=id)

        try:
            follow = FollowAuthor.objects.get(
                user=user, following_id=following
            )
            follow.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except FollowAuthor.DoesNotExist:
            return Response({
                'errors': 'Вы не были подписаны на этого автора'
            }, status=status.HTTP_400_BAD_REQUEST)


class FavoriteRecipeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)

        user = request.user

        favorite, created = FavoriteRecipe.objects.get_or_create(
            user=user, recipe=recipe
        )

        if created:
            serializer = serializers.ShortenedRecipeReadSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)

        user = request.user

        try:
            favorite_recipe = FavoriteRecipe.objects.get(user=user,
                                                         recipe=recipe)
            favorite_recipe.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не находиться в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ShoppingCartRecipeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)

        user = request.user

        cart, created = ShoppingCartRecipe.objects.get_or_create(
            user=user, recipe=recipe
        )

        if created:
            serializer = serializers.ShortenedRecipeReadSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'errors': 'Рецепт уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)

        user = request.user

        try:
            favorite_recipe = ShoppingCartRecipe.objects.get(
                user=user,
                recipe=recipe
            )
            favorite_recipe.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не находиться в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
