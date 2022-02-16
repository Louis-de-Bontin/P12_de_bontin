from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from datetime import datetime
import pytz
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from crm import permissions

from crm import serializers, models
from users.models import User as MODEL_USER

class CheckPathMixin:
    """
    Commun methods.
    """
    def check_path_user(self):
        """
        If the user try to access special methods through the /users/
        endpoint, it returns an error.
        """
        elements_path = self.request.get_full_path().split('/')
        if 'users' == elements_path[2]:
            message = 'Method not allowed with this path'
            raise PermissionDenied(message, code=403)

    def check_path_user_customer(self):
        """
        If the user try to access special methods through the /customer/
        endpoint, it returns an error.
        """
        elements_path = self.request.get_full_path().split('/')
        if 'users' == elements_path[2] or 'customers' == elements_path[2]:
            message = 'Method not allowed with this path'
            raise PermissionDenied(message, code=403)
    
    def check_path_sign(self):
        """
        If the user try to do anything else than sign with the /sign/
        endpoint, it returns an error.
        """
        try:
            elements_path = self.request.get_full_path().split('/')
            if 'sign' == elements_path[4]:
                if self.request.method != 'POST':
                    message = 'Method not allowed'
                    raise PermissionDenied(message, code=403)
        except:
            pass

class CustomerViewset(CheckPathMixin, ModelViewSet):
    serializer_class = serializers.CustomerListSerializer
    detail_serializer_class = serializers.CustomerDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,
                    permissions.CustomerPermissions]

    def fetch_queryset(self):
        """
        The queryset is a bit complicated. This is here that most of the security happens.
        It checks the path, the status of the connected user and returns the appropriate
        queryset.
        A MANAGER can pretty much see everything, but a SELLER can only see the customers
        he is in charge of, and a SUPPORT member can only see the customer he is related
        with throungh a contract.
        """
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
                    return models.Customer.objects.filter(seller=user)
                elif user.role == 'SUPPORT':
                    customers_list = models.Contract.objects.filter(
                                support=user).values('customer')
                    return models.Customer.objects.filter(
                                id__in=customers_list)
            else:
                """
                Only a MANAGER can access the /users/ endpoint and his extentions.
                """
                message = 'You are not authorized to perform this action'
                raise PermissionDenied(message, code=403)
        else:
            if is_manager:
                return models.Customer.objects.all()
            elif current_user.role == 'SELLER':
                return models.Customer.objects.filter(seller=current_user)
            elif current_user.role == 'SUPPORT':
                customers_list = models.Contract.objects.filter(
                            support=current_user).values('customer')
                return models.Customer.objects.filter(id__in=customers_list)
    
    def get_queryset(self):
        print(self.request.user.id)
        queryset = self.fetch_queryset()
        last_name = self.request.query_params.get('last_name')
        compagny_name = self.request.query_params.get('compagny_name')
        email = self.request.query_params.get('email')
        
        queryset = queryset.filter(last_name__icontains=last_name
                            ) if last_name != None and last_name != '' else queryset
        queryset = queryset.filter(compagny_name__icontains=compagny_name
                            ) if compagny_name != None and compagny_name != '' else queryset
        queryset = queryset.filter(email__icontains=email
                            ) if email != None and email != '' else queryset

        return queryset

    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """
        It checks the path because it is only possible to create a customer from
        the /customers/ endpoint. Same thing for update and destroy.
        Only a SELLER or a MANAGER is allowed to perform this action.
        """
        self.check_path_user()
        if self.request.user.role == 'SELLER':
            serializer.save(seller=self.request.user)
        
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        self.check_path_user()
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        self.check_path_user()
        return super().perform_destroy(instance)


class ContractViewset(CheckPathMixin, ModelViewSet):
    serializer_class = serializers.ContractListSerializer
    detail_serializer_class = serializers.ContractDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,
                    permissions.ContractPermissions]

    def fetch_queryset(self):
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
        self.check_path_sign()
        current_user = self.request.user
        is_manager = current_user.role == 'MANAGER'

        if 'users' == elements_path[2]:
            if is_manager:
                user = get_object_or_404(MODEL_USER, id=self.kwargs['user_pk'])
                if user.role == 'MANAGER':
                    message = 'This user is manager, therefore he is in charge of no customer'
                    raise NotFound(detail=message, code=404)
                else:
                    return models.Contract.objects.filter(Q(seller=user) | Q(support=user))
            else:
                message = 'You are not authorized to perform this action'
                raise PermissionDenied(message, code=403)
        
        elif 'customers' == elements_path[2]:
            customer = get_object_or_404(models.Customer,
                            id=self.kwargs['customer_pk'])
            if is_manager:
                return models.Contract.objects.filter(customer=customer)
            else:
                return models.Contract.objects.filter(
                    Q(customer=customer) & (Q(seller=current_user) | Q(support=current_user)))    
        
        else:
            if is_manager:
                return models.Contract.objects.all()
            else:
                return models.Contract.objects.filter(Q(seller=current_user) | Q(support=current_user))

    def get_queryset(self):
        queryset = self.fetch_queryset()
        last_name = self.request.query_params.get('last_name')
        compagny_name = self.request.query_params.get('compagny_name')
        date = self.request.query_params.get('date')
        due_low = self.request.query_params.get('due_low')
        due_high = self.request.query_params.get('due_high')

        queryset = queryset.filter(customer__last_name__icontains=last_name
                            ) if last_name != None and last_name != '' else queryset
        queryset = queryset.filter(customer__compagny_name__icontains=compagny_name
                            ) if compagny_name != None and compagny_name != '' else queryset
        queryset = queryset.filter(date_created__icontains=date
                            ) if date != None and date != '' else queryset
        queryset = queryset.filter(due__gt=float(due_low)
                            ) if due_low != None and due_low != '' else queryset
        queryset = queryset.filter(due__lt=float(due_high)
                            ) if due_high != None and due_high != '' else queryset
        return queryset
    
    def get_serializer_class(self):
        if (self.action == 'retrieve' or self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return self.detail_serializer_class
        if self.action == 'list':
            return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """
        A user can only create a contract from the /contracts/ endpoint.
        If the user is MANAGER, he needs to choose who will be the seller, the customer
        and the support member. If he is a SELLER, the seller is automaticly associated
        with him. A SUPPORT can't create a contract.
        This function also check if the support and seller selected are really SELLER
        and SUPPORT, otherwise it raises an error.
        """
        self.check_path_user_customer()
        self.check_fields()
        if self.request.user.role == 'MANAGER':
            if 'support' not in self.request.POST or 'customer' not in self.request.POST or 'seller' not in self.request.POST:
                message = 'Missing fields (support, customer or seller)'
                raise PermissionDenied(message, code=403)
            seller = self.check_role('SELLER')
        
        if self.request.user.role == 'SELLER':
            seller = self.request.user
        
        support = self.check_role('SUPPORT')
        
        customer = get_object_or_404(models.Customer, id=self.request.POST['customer'])
        if customer.existing == False:
            customer.existing = True
            customer.save()
        
        serializer.save(support=support, customer=customer, seller=seller)
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """
        Do pretty much the save stuff and same verification than the create action.
        """
        self.check_path_user_customer()
        self.check_fields()
        
        if 'support' in self.request.POST:
            support = self.check_role('SUPPORT')
            serializer.save(support=support)
        
        if 'seller' in self.request.POST:
            seller = self.check_role('SELLER')
            serializer.save(seller=seller)

        if 'customer' in self.request.POST:
            customer = get_object_or_404(models.Customer.objects.get(
                            id=self.request.POST['customer']))
            serializer.save(customer=customer)

        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """
        A contract is not directly deletable. A user must destroy an event, and
        the contract will be deleted in cascade.
        """
        message = 'You can not errase a contract'
        raise PermissionDenied(message, code=403)
    
    def check_fields(self):
        """
        Some fields must only be automaticly updatable. This method secure those
        fields.
        """
        forbiden_elements = ['event', 'signed', 'date_signed']
        for ele in forbiden_elements:
            if ele in self.request.POST:
                message = 'You are trying to update unupdatable fields'
                raise PermissionDenied(message, code=403)

    def check_role(self, role):
        user = get_object_or_404(MODEL_USER, id=self.request.POST[role.lower()])
        if user.role != role:
            message = 'The support selected is not SUPPORT'
            raise PermissionDenied(message, code=403)
        return user

class EventViewset(CheckPathMixin, ModelViewSet):
    serializer_class = serializers.EventListSerializer
    detail_serializer_class = serializers.EventDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,
                    permissions.EventPermission]

    def fetch_queryset(self):
        """
        The queryset is similar than for the customers and contracts. Only a MANAGER
        can acces the /user/ extentions endpoint.
        A SELLER can only see the events related to his customers, and a SUPPORT member
        can only see the event he is in charge of (throung a contract).
        """
        elements_path = self.request.get_full_path().split('/')
        self.check_path_sign()
        current_user = self.request.user
        is_manager = current_user.role == 'MANAGER'

        if 'users' == elements_path[2]:
            if is_manager:
                user = get_object_or_404(MODEL_USER, id=self.kwargs['user_pk'])
                if user.role == 'MANAGER':
                    raise NotFound(detail='This user is manager, therefore he is in charge of no event', code=404)
                else:
                    print('slt')
                    events_list = models.Contract.objects.filter(Q(seller=user) | Q(support=user)).values('event')
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
                return models.Event.objects.filter(id__in=events_list)

    def get_queryset(self):
        queryset = self.fetch_queryset()
        last_name = self.request.query_params.get('last_name')
        compagny_name = self.request.query_params.get('compagny_name')
        email = self.request.query_params.get('email')
        date = self.request.query_params.get('date')

        queryset_contract_last_name = models.Contract.objects.filter(
                    event__in=queryset, customer__last_name__icontains=last_name).values(
                                'event') if last_name != None and last_name != '' else queryset
        queryset = models.Event.objects.filter(id__in=queryset_contract_last_name)

        queryset_contract_compagny_name = models.Contract.objects.filter(
                    event__in=queryset, customer__compagny_name__icontains=compagny_name).values(
                                'event') if compagny_name != None and compagny_name != '' else queryset
        queryset = models.Event.objects.filter(id__in=queryset_contract_compagny_name)

        queryset_contract_email = models.Contract.objects.filter(
                    event__in=queryset, customer__email__icontains=email).values(
                                'event') if email != None and email != '' else queryset
        queryset = models.Event.objects.filter(id__in=queryset_contract_email)

        queryset = queryset.filter(date_event__icontains=date
                                ) if date != None and date != '' else queryset
        return queryset
    
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
        self.check_path_user_customer()
        contract = get_object_or_404(models.Contract, id=self.kwargs['contract_pk'])
        if contract.signed:
            message = 'This contract is already signed'
            raise PermissionDenied(message, code=403)

        event = serializer.save(finished=False)
        contract.event = event
        contract.signed = True
        contract.date_signed = pytz.UTC.localize(datetime.now())
        contract.save()
        return event
    
    def perform_update(self, serializer):
        """
        Prevent a user from updating a finished event.
        """
        self.check_path_user_customer()
        event = get_object_or_404(models.Event, id=self.kwargs['pk'])
        if event.finished:
            message = 'Can\'t update a finished event'
            raise PermissionDenied(message, code=403)
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """
        Deleting an event also delete the associated contract.
        Only a MANAGER can perform this action.
        """
        self.check_path_user_customer()
        return super().perform_destroy(instance)
        