# Generated by Django 5.1.4 on 2024-12-25 06:30

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('measurement_unit', models.CharField(choices=[('gram', 'г'), ('milliliter', 'мл'), ('item', 'шт.'), ('teaspoon', 'ч. л.'), ('drop', 'капля'), ('slice', 'кусок')], max_length=10, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'default_related_name': 'ingredients',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='')),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': 'Теги',
                'default_related_name': 'tags',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Изображение')),
                ('text', models.TextField(verbose_name='Текст')),
                ('cooking_time', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления')),
                ('Cart', models.ManyToManyField(related_name='recipes_in_cart', to=settings.AUTH_USER_MODEL, verbose_name='Корзина')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('favourite', models.ManyToManyField(related_name='favourites_recipe', to=settings.AUTH_USER_MODEL, verbose_name='Избранное')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='Количество')),
                ('ingredient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.ingredient')),
                ('recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.RecipeIngredient', to='recipes.ingredient', verbose_name='Игредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.tag', verbose_name='Теги'),
        ),
    ]
