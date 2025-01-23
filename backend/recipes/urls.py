from django.urls import path, register_converter

from recipes.converters import HexConverter
from recipes.views import recipe_redirect

register_converter(HexConverter, 'hex')


urlpatterns = [
    path('<hex:recipe_id>', recipe_redirect, name='shortlink')
]
