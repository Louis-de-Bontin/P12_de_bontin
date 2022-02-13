from django.shortcuts import get_object_or_404, get_list_or_404
from django.core import exceptions
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import pytz
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from crm import permissions

from crm import serializers, models
from users.models import User as MODEL_USER


class CustomerViewset(ModelViewSet):
    serializer_class = serializers.CustomerListSerializer
    detail_serializer_class = serializers.CustomerDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,
        permissions.CustomerPermissions]

    def get_queryset(self):
        elements_path = self.request.get_full_path().split('/')
        current_user = self.request.user
        is_manager = current_user.role == 'MANAGER'

        if 'users' == elements_path[2]:
            if is_manager:
                user = get_object_or_404(MODEL_USER, id=self.kwargs['user_pk'])
                if user.role == 'MANAGER':
                    message = 'This user is manager, therefore he is in charge of no customer'
                    raise NotFound(detail=message, code=404)
                elif user.role == 'SELLER':
                    return get_list_or_404(models.Customer, seller=user)
                elif user.role == 'SUPPORT':
                    customers_list = models.Contract.objects.filter(
                                support=user).values('customer')
                    return models.Customer.objects.filter(
                                id__in=customers_list)
            else:
                message = 'You are not authorized to perform this action'
                raise PermissionDenied(message, code=403)
        else:
            if is_manager:
                return models.Customer.objects.all()
            elif current_user.role == 'SELLER':
                return get_list_or_404(models.Customer, seller=current_user)
            elif current_user.role == 'SUPPORT':
                customers_list = models.Contract.objects.filter(
                            support=current_user).values('customer')
                return models.Customer.objects.filter(id__in=customers_list)

    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'SELLER':
            serializer.save(seller=self.request.user)
        
        return super().perform_create(serializer)


class ContractViewset(ModelViewSet):
    serializer_class = serializers.ContractListSerializer
    detail_serializer_class = serializers.ContractDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.ContractPermissions
    ]

    def get_queryset(self):
        """
        Quite complicated because this Viewset is user by 3 endpoints, and they all have
        differents queryset.
        If the contracts are fetched through the user url, only a manager can acces a queryset,
        which is the list the contracts related to the user_pk.
        If teh contracts are fetched through the customer url, a manager access all the
        contracts related to that customer. The supports an sellers only acces the contracts
        that points to them.
        Same logic if the contracts are fetched withe the contract url, except that the contracts
        are not related to a customer anymore.
        """
        elements_path = self.request.get_full_path().split('/')
        current_user = self.request.user
        is_manager = current_user.role == 'MANAGER'

        if 'users' == elements_path[2]:
            if is_manager:
                user = MODEL_USER.objects.get(id=self.kwargs['user_pk'])
                if user.role == 'MANAGER':
                    message = 'This user is manager, therefore he is in charge of no customer'
                    raise NotFound(detail=message, code=404)
                else:
                    return get_list_or_404(models.Contract, Q(seller=user) | Q(support=user))
            else:
                message = 'You are not authorized to perform this action'
                raise PermissionDenied(message, code=403)
        
        elif 'customers' == elements_path[2]:
            customer = get_object_or_404(models.Customer,
                            id=self.kwargs['customer_pk'])
            if is_manager:
                return get_list_or_404(models.Contract, customer=customer)
            else:
                return get_list_or_404(
                    models.Contract,
                    Q(customer=customer) & (Q(seller=current_user) | Q(support=current_user))
                )    
        
        else:
            if is_manager:
                return models.Contract.objects.all()
            else:
                return get_list_or_404(
                    models.Contract,
                    Q(seller=current_user) | Q(support=current_user)
                )                  
    
    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        if 'support' not in self.request.POST or 'customer' not in self.request.POST:
            return Response({'Message': 'Support or customer field missing'},
                status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(
            support=MODEL_USER.objects.get(id=self.request.POST['support']),
            customer=models.Customer.objects.get(id=self.request.POST['customer']),
            seller=MODEL_USER.objects.get(id=self.request.POST['seller'])
        )
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        contract = models.Contract.objects.get(id=self.kwargs['pk'])
        forbiden_elements = [
            'event',
            'seller',
            'signed',
            'date_created',
            'date_updated',
            'date_signed'
        ]

        for ele in forbiden_elements:
            if ele in self.request.POST:
                raise exceptions.FieldError('You are trying to update unupdatable fields.')

        if 'support' in self.request.POST:
            serializer.save(support=MODEL_USER.objects.get(
                            id=self.request.POST['support']))
        if 'customer' in self.request.POST:
            serializer.save(customer=models.Customer.objects.get(
                            id=self.request.POST['customer']))
        
        serializer.save()
        return contract
    

class EventViewset(ModelViewSet):
    serializer_class = serializers.EventListSerializer
    detail_serializer_class = serializers.EventDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,
        permissions.EventPermission]

    def get_queryset(self):
        elements_path = self.request.get_full_path().split('/')
        current_user = self.request.user
        is_manager = current_user.role == 'MANAGER'

        if 'users' == elements_path[2]:
            if is_manager:
                user = get_object_or_404(MODEL_USER, id=self.kwargs['user_pk'])
                if user.role == 'MANAGER':
                    raise NotFound(detail='This user is manager, therefore he is in charge of no event', code=404)
                else:
                    events_list = models.Contract.objects.filter(Q(seller=user) | Q(support=user))
                    return models.Event.objects.filter(id__in=events_list)
            else:
                raise PermissionDenied('You are not authorized to perform this action', code=403)
        
        elif 'customers' == elements_path[2]:
            customer = get_object_or_404(models.Customer, id=self.kwargs['customer_pk'])
            if is_manager:
                events_list = models.Contract.objects.filter(
                                customer=customer).values('event')
            elif current_user.role == 'SELLER':
                events_list = models.Contract.objects.filter(
                    Q(customer=customer) & Q(seller=current_user)).values('event')
            elif current_user.role == 'SUPPORT':
                events_list = models.Contract.objects.filter(
                    Q(customer=customer) & Q(support=current_user)).values('event')
            return models.Event.objects.filter(id__in=events_list)
        
        else:
            if is_manager:
                return models.Event.objects.all()
            else:
                events_list = models.Contract.objects.filter(
                    Q(seller=current_user) | Q(support=current_user)).values('event')
                return models.Event.objects.filter(id_in=events_list)      
    
    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """
        Update the status of the contract when creating an event.
        """
        contract = models.Contract.objects.get(id=self.kwargs['contract_pk'])
        if contract.signed:
            raise exceptions.FieldError('Contract already signed')

        event = serializer.save()
        contract.event = event
        contract.signed = True
        contract.date_signed = pytz.UTC.localize(datetime.now())
        contract.save()
        return event
    
    def perform_update(self, serializer):
        """
        Prevent a user from updating a finished event.
        """
        if models.Event.objects.get(id=self.kwargs['pk']).finished:
            raise exceptions.BadRequest("Can\'t update a finished event")
        return super().perform_update(serializer)
        