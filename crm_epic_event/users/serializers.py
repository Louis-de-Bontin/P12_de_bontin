from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import User


class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = User
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
        model = User
        fields = ['first_name', 'last_name', 'id']
