from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from foodgram.constants import (MEASUREMENT_UNITS, MEASUREMENT_UNITS_INDEX,
                                MIN_INGREDIENT_AMOUNT,
                                MIN_RECIPE_COOKING_TIME_VALUE,
                                STR_OUTPUT_LIMIT)
from recipes.abstracts import ModelWithName, RecipeUserModel

User = get_user_model()


class Tag(ModelWithName):
    slug = models.SlugField('Человекочитаемый ключ', unique=True)

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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='%(app_label)s_%(class)s_prevent_not_unique_name_and_unit'
            ),
        )


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

    @property
    def get_short_url(self):
        return reverse('shortlink', kwargs={'recipe_id': self.id})

    @property
    def get_absolute_url(self):
        return f'/recipes/{self.id}/'


class Cart(RecipeUserModel):

    class Meta(RecipeUserModel.Meta):
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        default_related_name = 'recipes_in_cart'


class Favourite(RecipeUserModel):

    class Meta(RecipeUserModel.Meta):
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'favourites_recipe'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL,
        related_name='in_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT), ]
    )

    class Meta:
        verbose_name = 'ингредент в рецепте'
        verbose_name_plural = 'Ингреденты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name=(
                    '%(app_label)s_%(class)s_prevent_not'
                    '_unique_ingredient_in_recipe'
                )
            ),
        )

    def __str__(self):
        return (
            f'{self.recipe.name} - {self.ingredient.name} : {self.amount}'
        )[:STR_OUTPUT_LIMIT]
