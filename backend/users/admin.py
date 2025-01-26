from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from foodgram.constants import USER_ADMIN_ADD_FIELDSET
from users.models import Subscribe

User = get_user_model()


class AvatarListFilter(admin.SimpleListFilter):
    title = ('аватар')
    parameter_name = 'is_have_avatar'

    def lookups(self, request, model_admin):
        return [
            ('avatar', ('Да')),
            ('empty', ('Нет'))
        ]

    def queryset(self, request, queryset):
        if self.value() == 'avatar':
            return queryset.exclude(
                avatar=''
            )
        if self.value() == 'empty':
            return queryset.filter(
                avatar=''
            )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribe_to')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = ((None, {'fields': ('avatar',)}), ) + BaseUserAdmin.fieldsets
    list_display = (
        BaseUserAdmin.list_display
        + ('total_subscribes', 'total_recipes', 'avatar_field')
    )
    list_filter = BaseUserAdmin.list_filter + (AvatarListFilter, )
    search_fields = ('username', 'first_name', 'email')
    add_fieldsets = USER_ADMIN_ADD_FIELDSET

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('subscribes', 'recipes')

    @admin.display(description='Подписчиков')
    def total_subscribes(self, obj):
        return obj.subscribes.count()

    @admin.display(description='Рецептов')
    def total_recipes(self, obj):
        return obj.recipes.count()

    @admin.display(description='Аватар')
    def avatar_field(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img style="max-width: 150px;" src="{obj.avatar.url}" />'
            )
        return 'Нет аватара'
