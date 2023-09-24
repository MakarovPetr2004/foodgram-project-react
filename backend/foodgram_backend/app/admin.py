from django.contrib import admin

from app import models


class BaseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(models.Tag)
class TagAdmin(BaseAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(BaseAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(models.RecipeTag)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')
    list_editable = ('tag',)


@admin.register(models.RecipeIngredient)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_editable = ('ingredient',)


class TagRecipeInline(admin.TabularInline):
    model = models.Recipe.tags.through


class IngredientRecipeInline(admin.TabularInline):
    model = models.Recipe.ingredients.through


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_tags', 'text', 'get_ingredients',
                    'cooking_time', 'created', 'get_favorites_count')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('name', 'author__username')
    empty_value_display = '-пусто-'
    inlines = [TagRecipeInline, IngredientRecipeInline]

    def get_tags(self, obj):
        tags_qs = obj.tags.all()
        return ', '.join(tags_qs.values_list('name', flat=True))

    get_tags.short_description = 'Тег'

    def get_ingredients(self, obj):
        ingredients_qs = obj.ingredients.all()
        return ', '.join(ingredients_qs.values_list('name', flat=True))

    get_ingredients.short_description = 'Ингредиент'

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'Добавления в избранное'


@admin.register(models.FollowAuthor)
class FollowAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_editable = ('following',)


@admin.register(models.FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_editable = ('recipe',)


@admin.register(models.ShoppingCartRecipe)
class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_editable = ('recipe',)
