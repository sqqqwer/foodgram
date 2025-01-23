from django.http import HttpResponsePermanentRedirect

from recipes.models import Recipe


def recipe_redirect(request, recipe_id):
    recipe = Recipe.objects.filter(pk=recipe_id)
    if not recipe.count():
        return HttpResponsePermanentRedirect('/not-found/')
    return HttpResponsePermanentRedirect(recipe.first().get_absolute_url)
