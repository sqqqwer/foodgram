import urllib.parse

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilterSet
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (AvatarSerializer, CartSerializer,
                             CreateRecipeSerializer, CreateUserSerializer,
                             FavouriteSerializer, IngredientSerializer,
                             ReadRecipeSerializer, RecipeShortSerializer,
                             SubscribeSerializer, TagSerializer,
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


class UserViewSet(BaseUserViewSet):
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        return User.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(methods=['get'], detail=False, url_path='me')
    def me(self, request):
        self.get_object = lambda: self.request.user
        return self.retrieve(request)

    @action(methods=["post"], detail=False)
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, request):
        queryset = self.get_queryset().filter(
            subscribes__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        )
        self.get_queryset = lambda: queryset
        self.get_serializer_class = lambda: UserSubscribeSerializer
        return self.list(request)

    @action(methods=['post'], detail=True, url_path='subscribe')
    def subscribe(self, request, id):
        subscribe_user = self._get_subscribe_target_user(id)
        data = {
            'user': request.user.id,
            'subscribe_to': subscribe_user.id
        }
        new_subscribe = SubscribeSerializer(data=data)
        new_subscribe.is_valid(raise_exception=True)
        new_subscribe.save()
        self.get_serializer_class = lambda: UserSubscribeSerializer
        serializer = self.get_serializer(subscribe_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        subscribes = self._get_subscribe_target_user(id)
        subscriber_deleted, _ = Subscribe.objects.filter(
            user=request.user,
            subscribe_to=subscribes
        ).delete()
        status_code = (
            status.HTTP_204_NO_CONTENT
            if subscriber_deleted
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(status=status_code)

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        self.get_object = lambda: self.request.user
        self.get_serializer_class = lambda: AvatarSerializer
        return self.partial_update(request)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        self.request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_subscribe_target_user(self, pk):
        return get_object_or_404(
            User.objects.annotate(
                recipes_count=Count('recipes')
            ),
            pk=pk
        )

    def _get_current_user_object(self, id):
        return User.objects.get(id=id)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'tags', 'ingredients'
    ).select_related('author')
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet
    search_fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(recipe.get_short_url)
        return Response({'short-link': short_link})

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
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
    def shopping_cart(self, request, pk):
        return self._add_related_item(pk, CartSerializer, request.user)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self._delete_related_item(
            pk,
            Cart,
            request.user
        )

    @action(methods=['post'], detail=True, url_path='favorite')
    def favorite(self, request, pk):
        return self._add_related_item(pk, FavouriteSerializer, request.user)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self._delete_related_item(
            pk,
            Favourite,
            request.user
        )

    def _add_related_item(self, recipe_pk, serializer, user):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        data = {
            'user': user.id,
            'recipe': recipe.id
        }
        new_related_item = serializer(data=data)
        new_related_item.is_valid(raise_exception=True)
        new_related_item.save()
        _serializer = RecipeShortSerializer(recipe)
        return Response(_serializer.data, status=status.HTTP_201_CREATED)

    def _delete_related_item(self, recipe_pk, model, user):
        item_deleted, _ = model.objects.filter(
            user=user,
            recipe_id=recipe_pk
        ).delete()
        status_code = (
            status.HTTP_204_NO_CONTENT
            if item_deleted
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(status=status_code)
