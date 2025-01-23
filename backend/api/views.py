import urllib.parse

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilterSet
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (AvatarSerializer, CreateUserSerializer,
                             IngredientSerializer, RecipeSerializer,
                             RecipeShortSerializer, TagSerializer,
                             UserSerializer, UserSubscribeSerializer)
from api.utils import get_ingredients_string_from_user_cart
from recipes.models import Cart, Favourite, Ingredient, Recipe, Tag
from users.models import Subscribe

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', 'name')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = None
    serializer_class = TagSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return User.objects.annotate(
            recipes_count=Count('recipes')
        ).order_by('-id')

    def get_permissions(self):
        permission_class = self.get_permission_class()
        return [permission_class()]

    def get_permission_class(self):
        if self.action in ('list', 'create', 'retrieve'):
            return AllowAny
        return IsAuthenticated

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        elif self.action in ('subscriptions', 'subscribe'):
            return UserSubscribeSerializer
        elif self.action == 'avatar':
            return AvatarSerializer
        return UserSerializer

    @action(methods=['get'], detail=False, url_path='me')
    def me(self, request, *args, **kwargs):
        self.get_object = lambda: self.request.user
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            subscribes__user=request.user
        )
        self.get_queryset = lambda: queryset
        return self.list(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path='subscribe')
    def subscribe(self, request, pk):
        subscribe_user = self._get_subscribe_target_user(pk)
        new_subscribe = Subscribe(
            user=request.user,
            subscribe_to=subscribe_user
        )
        try:
            new_subscribe.full_clean()
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        new_subscribe.save()
        serializer = self.get_serializer(subscribe_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        subscribes = self._get_subscribe_target_user(pk)
        subscribtion = Subscribe.objects.filter(
            user=request.user,
            subscribe_to=subscribes
        )
        if not len(subscribtion):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscribtion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def avatar(self, request, *args, **kwargs):
        self.get_object = lambda: self.request.user
        return self.partial_update(request, *args, **kwargs)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self._get_current_user_object(request.user.id)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_subscribe_target_user(self, pk):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=pk)

    def _get_current_user_object(self, id):
        return User.objects.get(id=id)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet

    def get_permissions(self):
        permission_class = self.get_permission_class()
        return [permission_class()]

    def get_serializer_class(self):
        if self.action in ('shopping_cart', 'favorite'):
            return RecipeShortSerializer
        return RecipeSerializer

    def get_permission_class(self):
        if self.action == 'download_shopping_cart':
            return IsAuthenticated
        return IsAuthorOrAdminOrReadOnly

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(recipe.get_short_url)
        return Response({'short-link': short_link})

    @action(methods=['get'], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients_string = get_ingredients_string_from_user_cart(
            request.user
        )
        content_type = 'text/plain'
        file_name = 'Ingredient%20list.txt'
        file_name = urllib.parse.unquote(file_name)
        response = HttpResponse(ingredients_string, content_type=content_type)
        response["Content-Disposition"] = (
            'attachment; filename=Ingredient list.txt'
        )
        return response

    @action(methods=['post'], detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        return self._add_related_item(kwargs['pk'], Cart, request.user)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        return self._delete_related_item(
            kwargs['pk'],
            request.user.cart_set.all()
        )

    @action(methods=['post'], detail=True, url_path='favorite')
    def favorite(self, request, *args, **kwargs):
        return self._add_related_item(kwargs['pk'], Favourite, request.user)

    @favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        return self._delete_related_item(
            kwargs['pk'],
            request.user.favourite_set.all()
        )

    def _add_related_item(self, recipe_pk, model, user):
        queryset = self.get_queryset()
        recipe = get_object_or_404(queryset, pk=recipe_pk)
        new_item = model(
            user=user,
            recipe=recipe
        )
        try:
            new_item.full_clean()
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        new_item.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_related_item(self, recipe_pk, items_queryset):
        queryset = self.get_queryset()
        recipe = get_object_or_404(queryset, pk=recipe_pk)
        item_recipe = items_queryset.filter(recipe=recipe)
        if not len(item_recipe):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        item_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
