from app import models
from django.contrib import admin


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagRecipeInline(admin.TabularInline):
    model = models.Recipe.tags.through


class IngredientRecipeInline(admin.TabularInline):
    model = models.Recipe.ingredients.through


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        TagRecipeInline,
        IngredientRecipeInline
    ]
    list_display = (
        'name',
        'author',
        'get_tags',
        'text',
        'get_ingredients',
        'cooking_time',
        'created',
        'get_favorites_count'
    )
    search_fields = ('name', 'author', 'tags__name')
    list_filter = ('name', 'author__username')
    empty_value_display = '-пусто-'

    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    get_tags.short_description = 'Тег'

    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиент'

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'Добавления в избранное'


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')
    list_editable = ('tag',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_editable = ('ingredient',)


class FollowAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_editable = ('following',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_editable = ('recipe',)


class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_editable = ('recipe',)


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.RecipeTag, TagRecipeAdmin)
admin.site.register(models.RecipeIngredient, IngredientRecipeAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.FollowAuthor, FollowAuthorAdmin)
admin.site.register(models.FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(models.ShoppingCartRecipe, ShoppingCartRecipeAdmin)
