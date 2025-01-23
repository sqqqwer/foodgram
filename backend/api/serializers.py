from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

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
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }
        model = User

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ('avatar', )
        model = User

    def validate(self, attrs):
        field_data = attrs.get('avatar')
        if not field_data:
            raise serializers.ValidationError({'avatar': 'Обязательное поле.'})
        return super().validate(attrs)

    def validate_avatar(self, value):
        if value is None:
            raise serializers.ValidationError('Нет Изображения.')
        return value


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, subscribe_to=obj.id).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')
        model = Recipe

    def get_is_subscribed(self, obj):
        return True


class UserSubscribeSerializer(UserSerializer):
    recipes = RecipeShortSerializer(
        read_only=True,
        many=True
    )
    recipes_count = serializers.IntegerField(default=0)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        model = User

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipes_limit = (
            self.context.get('request')
            .query_params.get('recipes_limit')
        )
        if recipes_limit:
            data['recipes'] = data['recipes'][:int(recipes_limit)]
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT), ]
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient

    def to_representation(self, instance):
        response = IngredientSerializer(
        ).to_representation(instance)
        return response


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False
    )
    ingredients = RecipeIngredientSerializer(many=True, allow_empty=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(allow_null=False, allow_empty_file=False)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe

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
        return super().validate(attrs)

    def validate_tags(self, value):
        unique_tags = []
        for tag in value:
            if tag in unique_tags:
                raise serializers.ValidationError('Не уникальный Тег.')
            unique_tags.append(tag)
        return value

    def validate_ingredients(self, value):
        unique_ingredients = []
        for ingredient in value:
            if ingredient['ingredient'] in unique_ingredients:
                raise serializers.ValidationError('Не уникальный Ингредиент.')
            unique_ingredients.append(ingredient['ingredient'])
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

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
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['tags'] = TagSerializer(many=True).to_representation(
            instance.tags
        )
        for i in range(len(response['ingredients'])):
            ingredient_id = response['ingredients'][i]['id']
            response['ingredients'][i]['amount'] = (
                RecipeIngredient.objects.get(
                    recipe_id=instance.id,
                    ingredient_id=ingredient_id
                ).amount
            )
        return response
