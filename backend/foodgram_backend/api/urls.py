from api import views
from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('users', views.NewUserViewSet, basename='users')
router_v1.register('tags', views.TagViewSet, basename='tags')
router_v1.register(
    'ingredients', views.IngredientViewSet, basename='ingredients'
)
router_v1.register('recipes', views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        views.FollowAuthorView.as_view(),
        name='subscribe'
    ),
    path(
        'recipes/<int:id>/favorite/',
        views.FavoriteRecipeView.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        views.ShoppingCartRecipeView.as_view(),
        name='cart'
    ),
    path('', include(router_v1.urls)),
    path('users/me/', views.NewUserViewSet.as_view({'get': 'me'})),
    path('users/set_password/', UserViewSet.as_view({'get': 'set_password'})),
    path('auth/', include('djoser.urls.authtoken')),
]
