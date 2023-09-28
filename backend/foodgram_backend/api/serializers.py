from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.fields import Base64ImageField
from app import models, validators

User = get_user_model()


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
            return models.FollowAuthor.objects.filter(
                user=user, following=obj
            ).exists()


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
    amount = serializers.IntegerField(
        source='recipe_ingredient_amount',
        validators=[validators.validate_positive]
    )

    class Meta:
        model = models.Ingredient
        fields = ('id', 'amount')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = IsSubUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        source='recipe_ingredient', many=True
    )
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
    def validate_ingredients(value):
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return value

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        recipe_ingredients = []
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('recipe_ingredient_amount')
            recipe_ingredients.append(
                models.RecipeIngredient(
                    ingredient_id=ingredient_id, recipe=recipe, amount=amount
                )
            )

        models.RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @staticmethod
    def create_tags(recipe, tags_data):
        recipe_tags = []
        for tag in tags_data:
            recipe_tags.append(models.RecipeTag(tag=tag, recipe=recipe))

        models.RecipeTag.objects.bulk_create(recipe_tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = models.Recipe.objects.create(**validated_data)

        self.create_ingredients(recipe, ingredients)
        self.create_tags(recipe, tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        super().update(instance, validated_data)

        instance.recipe_ingredient.all().delete()
        instance.recipe_tag.all().delete()

        self.create_ingredients(instance, ingredients)
        self.create_tags(instance, tags)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class UserRecipeSerializer(IsSubUserSerializer, serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()

    class Meta(IsSubUserSerializer.Meta):
        fields = IsSubUserSerializer.Meta.fields + (
            'recipes_count',
            'recipes'
        )

    def get_recipes_count(self, obj):
        count = obj.recipes.count()
        return count

    def to_representation(self, instance):
        data = super().to_representation(instance)
        max_recipes = int(self.context['request'].query_params.get(
            'recipes_limit', 3))
        recipes = instance.recipes.all()[:max_recipes]
        serialized_recipes = ShortenedRecipeReadSerializer(
            recipes, many=True).data
        data['recipes'] = serialized_recipes
        return data
