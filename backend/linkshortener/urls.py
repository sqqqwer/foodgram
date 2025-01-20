from django.urls import path, register_converter

from linkshortener.views import recipe_redirect
from linkshortener.converters import HexConverter

register_converter(HexConverter, 'hex')


urlpatterns = [
    path('<hex:recipe_id>', recipe_redirect, name='shortlink')
]
