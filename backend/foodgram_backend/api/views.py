from django.db.models import Q
from djoser.views import UserViewSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from api.serializers import TagSerializer, IngredientSerializer
from app.models import Tag, Ingredient


class NewUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post']

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    pagination_class = LimitOffsetPagination
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('name', '').strip()

        if search_term:
            startswith_results = queryset.filter(name__istartswith=search_term)
            contains_results = queryset.filter(
                name__icontains=search_term).exclude(id__in=startswith_results)
            sorted_results = list(startswith_results) + list(contains_results)
            return sorted_results
        return queryset
