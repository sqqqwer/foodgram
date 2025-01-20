from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls))
]
