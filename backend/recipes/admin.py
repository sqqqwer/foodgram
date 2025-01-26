from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from recipes.abstracts import RecipeUserAdmin
from recipes.models import (Cart, Favourite, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class IngredientTabular(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_link', 'ingredients_link',
                    'tags_link', 'count_in_favourites')
    list_filter = ('tags', )
    list_select_related = ('author',)
    inlines = (IngredientTabular, )
    search_fields = ('name', 'author__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('tags', 'ingredients')

    @admin.display(description='В избранных у')
    def count_in_favourites(self, obj):
        return obj.favourites_recipe.count()

    @admin.display(description='Теги')
    def tags_link(self, obj):
        return self._get_many_objects_links_html(
            obj.tags.all()
        )

    @admin.display(description='Автор')
    def author_link(self, obj):
        author = obj.author
        return self._get_object_link_html(author, author.username)

    @admin.display(description='Ингредиенты')
    def ingredients_link(self, obj):
        return self._get_many_objects_links_html(
            obj.ingredients.all()
        )

    def _get_many_objects_links_html(self, queryset):
        result = []
        for item in queryset:
            result.append(
                self._get_object_link_html(item, item.name)
            )
        return mark_safe(', '.join(result))

    def _get_object_link_html(self, obj, link_text):
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=(obj.id,)
        )
        return mark_safe(f'<a href="{url}">{link_text}</a>')


@admin.register(Cart)
class CartAdmin(RecipeUserAdmin):
    pass


@admin.register(Favourite)
class FavouriteAdmin(RecipeUserAdmin):
    pass


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('ingredient__name', )
    list_select_related = ('ingredient', )
