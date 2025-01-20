from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterSet(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_favorited_recipes'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_recipes'
    )
    author = filters.AllValuesFilter(field_name='author__id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def get_favorited_recipes(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favourites_recipe__user=self.request.user)
        return queryset

    def get_shopping_cart_recipes(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(recipes_in_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
