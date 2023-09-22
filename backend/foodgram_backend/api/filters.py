import django_filters

from app.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(
        field_name='author__id', lookup_expr='exact'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='exact',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('name', 'tags',)
