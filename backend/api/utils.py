from django.db.models import Sum

from recipes.models import RecipeIngredient


def get_ingredients_string_from_user_cart(user):
    ingredients = RecipeIngredient.objects.filter(
        recipe__recipes_in_cart__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(total_amount=Sum('amount'))
    result_string = ''
    for ingredient in ingredients:
        ingredient_dict = (
            f'{ingredient["ingredient__name"]}'
            f' - {ingredient["total_amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}.\n'
        )
        result_string += ingredient_dict
    return result_string
