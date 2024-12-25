from django.db import models

from foodgram.constants import STANDART_CHAR_MAX_LENGHT, STR_OUTPUT_LIMIT


class ModelWithName(models.Model):
    name = models.CharField('Название', max_length=STANDART_CHAR_MAX_LENGHT)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:STR_OUTPUT_LIMIT]
