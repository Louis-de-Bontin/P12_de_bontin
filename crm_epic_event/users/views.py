from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from users import serializers, models

class UserViewset(ModelViewSet):
    serializer_class = serializers.UserListSerializer
    detail_serializer_class = serializers.UserDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return models.User.objects.all()
    
    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        if serializer.validated_data['role'] == 'MANAGER':
            serializer.validated_data['is_superuser'] = True
        super().perform_create(serializer)
