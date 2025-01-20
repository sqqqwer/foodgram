from django.contrib.auth import get_user_model
from django.db import models

from foodgram.constants import STANDART_CHAR_MAX_LENGHT, STR_OUTPUT_LIMIT


User = get_user_model()

class ModelWithName(models.Model):
    name = models.CharField('Название', max_length=STANDART_CHAR_MAX_LENGHT)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:STR_OUTPUT_LIMIT]


class RecipeUserModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_prevent_not_unique_object'
            ),
        )
