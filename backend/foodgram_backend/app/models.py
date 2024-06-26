from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models

from constants import NAME_SLUG_MEAS_UNIT_LENGTH
from .validators import validate_positive

User = get_user_model()


class Name(models.Model):
    name = models.CharField('Название', max_length=NAME_SLUG_MEAS_UNIT_LENGTH)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(Name):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=NAME_SLUG_MEAS_UNIT_LENGTH
    )

    class Meta(Name.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'


class Tag(Name):
    name = models.CharField(
        'Название',
        max_length=NAME_SLUG_MEAS_UNIT_LENGTH, unique=True
    )
    color = models.CharField(
        'Цвет', max_length=7, unique=True, validators=[MinLengthValidator(7)]
    )
    slug = models.SlugField(
        'Ссылка', max_length=NAME_SLUG_MEAS_UNIT_LENGTH, unique=True
    )

    class Meta(Name.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'


class Recipe(Name):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField('Изображение', upload_to='recipes/images')
    text = models.TextField('Текст')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Теги рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[validate_positive],
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta(Name.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('created',)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_combination_recipe_tag'
            )
        ]
        default_related_name = 'recipe_tag'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[validate_positive]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination_recipe_ingredient'
            )
        ]
        default_related_name = 'recipe_ingredient'


class FollowAuthor(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
        verbose_name = 'Подписчик автора'
        verbose_name_plural = 'Подписчики авторов'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Любимый рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class ShoppingCartRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
        verbose_name='Автор корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='added_to_cart_by',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe'
            )
        ]
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзинах'
