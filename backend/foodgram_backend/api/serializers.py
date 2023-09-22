import base64

from app import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IsSubUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if models.FollowAuthor.objects.filter(
                    user=user, following=obj).exists():
                return True
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(source='recipe_ingredient_amount')

    class Meta:
        model = models.Ingredient
        fields = ['id', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    author = IsSubUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = fields

    @staticmethod
    def get_ingredients(obj):
        recipe_ingredients = models.RecipeIngredient.objects.filter(recipe=obj)
        return [
            {
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'measurement_unit': ri.ingredient.measurement_unit,
                'amount': ri.amount
            }
            for ri in recipe_ingredients
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and models.FavoriteRecipe.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and models.ShoppingCartRecipe.objects.filter(
                    user=user, recipe=obj
                ).exists())


class ShortenedRecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
        allow_empty=False,

    )
    ingredients = IngredientRecipeSerializer(
        many=True,
        allow_empty=False,
    )
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    @staticmethod
    def _create_ingredients(recipe, ingredients_data):
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('recipe_ingredient_amount')
            current_ingredient = get_object_or_404(models.Ingredient,
                                                   pk=ingredient_id)
            models.RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )

    @staticmethod
    def _create_tags(recipe, tags_data):
        for tag in tags_data:
            models.RecipeTag.objects.create(tag=tag, recipe=recipe)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = models.Recipe.objects.create(**validated_data)

        self._create_ingredients(recipe, ingredients)
        self._create_tags(recipe, tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.recipe_ingredient.all().delete()
        instance.recipe_tag.all().delete()

        self._create_ingredients(instance, ingredients)
        self._create_tags(instance, tags)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class UserRecipeSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes'
        )
        read_only_fields = fields

    def get_recipes_count(self, obj):
        max_recipes = int(self.context['request'].query_params.get(
            'recipes_limit', 1))
        return max_recipes

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return models.FollowAuthor.objects.filter(
            user=user, following=obj).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        max_recipes = data.pop('recipes_count')
        recipes = instance.recipes.all()[:max_recipes]
        serialized_recipes = ShortenedRecipeReadSerializer(
            recipes, many=True).data
        data['recipes'] = serialized_recipes
        return data
