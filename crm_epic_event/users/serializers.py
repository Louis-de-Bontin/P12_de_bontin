from rest_framework.serializers import ModelSerializer

from users.models import User as MODEL_USER


class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = MODEL_USER
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'id',
            'phone',
            'role'
        ]        


class UserListSerializer(ModelSerializer):

    class Meta:
        model = MODEL_USER
        fields = ['first_name', 'last_name', 'id']
