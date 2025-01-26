from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.abstracts import RecipeUserSerializer
from foodgram.constants import MIN_INGREDIENT_AMOUNT
from recipes.models import (Cart, Favourite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscribe

User = get_user_model()


class ShortLinkSerializer(serializers.Serializer):

    short_link = serializers.URLField()

    class Meta:
        fields = ('short_link', )


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar', )

    def validate(self, attrs):
        field_data = attrs.get('avatar')
        if not field_data:
            raise serializers.ValidationError({'avatar': 'Обязательное поле.'})
        return super().validate(attrs)

    def validate_avatar(self, value):
        if value is None:
            raise serializers.ValidationError('Нет Изображения.')
        return value


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            BaseUserSerializer.Meta.fields
            + ('username', 'is_subscribed', 'avatar')
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(
            user=user.id, subscribe_to=obj.id).exists()


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class UserSubscribeSerializer(UserSerializer):
    recipes = RecipeShortSerializer(
        read_only=True,
        many=True
    )
    recipes_count = serializers.IntegerField(default=0)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request', False)
        if request and not request.user.is_anonymous:
            recipes_limit = request.query_params.get('recipes_limit')
            if isinstance(recipes_limit, str) and recipes_limit.isnumeric():
                data['recipes'] = data['recipes'][:int(recipes_limit)]
            return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT), ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        ingredient_data = IngredientSerializer().to_representation(
            instance.ingredient
        )
        ingredient_data['amount'] = instance.amount
        return ingredient_data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredients_in_recipes'
    )

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=user, recipe=obj.id).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False
    )
    ingredients = RecipeIngredientSerializer(many=True, allow_empty=False)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_image(self, value):
        if value is None:
            raise serializers.ValidationError('Нет Изображения.')
        return value

    def validate(self, attrs):
        fields = ('ingredients', 'tags')
        for field in fields:
            field_data = attrs.get(field)
            if not field_data:
                raise serializers.ValidationError(f'Нет поля {field}.')

        unique_tags = []
        for tag in attrs['tags']:
            if tag in unique_tags:
                raise serializers.ValidationError('Не уникальный Тег.')
            unique_tags.append(tag)

        unique_ingredients = []
        for ingredient in attrs['ingredients']:
            if ingredient['ingredient'] in unique_ingredients:
                raise serializers.ValidationError('Не уникальный Ингредиент.')
            unique_ingredients.append(ingredient['ingredient'])

        return super().validate(attrs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        request = self.context.get('request')
        validated_data['author'] = request.user

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        self._create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', False)
        if tags_data:
            instance.tags.set(tags_data)

        ingredients_data = validated_data.pop('ingredients', False)
        if ingredients_data:
            instance.ingredients.clear()
            self._create_ingredients(instance, ingredients_data)

        return super().update(instance, validated_data)

    def _create_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            context=self.context
        ).to_representation(instance)


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('user', 'subscribe_to')

    def validate(self, attrs):
        if attrs['user'] == attrs['subscribe_to']:
            raise serializers.ValidationError(
                {'subscribe_to': 'Нельзя подписаться на самого себя'}
            )
        return super().validate(attrs)


class CartSerializer(RecipeUserSerializer, serializers.ModelSerializer):

    class Meta(RecipeUserSerializer.Meta):
        model = Cart
        fields = RecipeUserSerializer.Meta.fields


class FavouriteSerializer(RecipeUserSerializer, serializers.ModelSerializer):

    class Meta(RecipeUserSerializer.Meta):
        model = Favourite
        fields = RecipeUserSerializer.Meta.fields
