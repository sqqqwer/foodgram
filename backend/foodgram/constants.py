STANDART_CHAR_MAX_LENGHT = 256
MIN_RECIPE_COOKING_TIME_VALUE = 1
STR_OUTPUT_LIMIT = 50
USER_EMAIL_MAX_LENGHT = 254
USER_CHAR_MAX_LENGHT = 150
MEASUREMENT_UNITS_INDEX = 0
MIN_INGREDIENT_AMOUNT = 1
PAGINATION_PAGE_SIZE = 6

MEASUREMENT_UNITS = (
    ('gram', 'г'),
    ('milliliter', 'мл'),
    ('item', 'шт.'),
    ('teaspoon', 'ч. л.'),
    ('drop', 'капля'),
    ('slice', 'кусок')
)

USER_ADMIN_ADD_FIELDSET = (
    (
        None,
        {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'usable_password', 'password1', 'password2'),
        },
    ),
)