from django.conf import settings
from django.shortcuts import redirect


def recipe_redirect(request, recipe_id):
    return redirect(f'https://{settings.SITE_DOMANE}/recipes/{recipe_id}/')
