from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (MEASUREMENT_UNITS, MEASUREMENT_UNITS_INDEX,
                                MIN_INGREDIENT_AMOUNT,
                                MIN_RECIPE_COOKING_TIME_VALUE)
from recipes.mixins import ModelWithName, RecipeUserModel

User = get_user_model()


class Tag(ModelWithName):
    slug = models.SlugField('', unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'


class Ingredient(ModelWithName):
    max_measurement_unit_length = max(
        len(role[MEASUREMENT_UNITS_INDEX]) for role in MEASUREMENT_UNITS
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        choices=MEASUREMENT_UNITS,
        max_length=max_measurement_unit_length
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'


class Recipe(ModelWithName):
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Игредиенты'
    )
    image = models.ImageField('Изображение', null=False, upload_to='recipes/')
    text = models.TextField('Текст')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(MIN_RECIPE_COOKING_TIME_VALUE), ]
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date', )


class Cart(RecipeUserModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_prevent_not_unique_object'
            ),
        )


class Favourite(RecipeUserModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites_recipe'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_prevent_not_unique_object'
            ),
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.SET_NULL
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT), ]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name=(
                    '%(app_label)s_%(class)s_prevent_not'
                    '_unique_ingredient_in_recipe'
                )
            ),
        )
