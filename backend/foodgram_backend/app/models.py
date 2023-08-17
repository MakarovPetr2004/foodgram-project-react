from django.contrib.auth import get_user_model
from django.db import models

from constants import NAME_SLUG_MEAS_UNIT_LENGTH
from .validators import validate_positive

User = get_user_model()


class Name(models.Model):
    name = models.CharField(max_length=NAME_SLUG_MEAS_UNIT_LENGTH)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(Name):

    class Meta(Name.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'


class Tag(Name):
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=NAME_SLUG_MEAS_UNIT_LENGTH, unique=True)

    class Meta(Name.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'


class Recipe(Name):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[validate_positive],
    )

    class Meta(Name.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[validate_positive])
    measurement_unit = models.CharField(max_length=NAME_SLUG_MEAS_UNIT_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination_recipe_ingredient'
            )
        ]
