from rest_framework.serializers import Serializer


class RecipeUserSerializer(Serializer):

    class Meta:
        fields = ('user', 'recipe')
