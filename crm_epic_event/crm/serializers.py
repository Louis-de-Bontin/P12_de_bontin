from rest_framework.serializers import ModelSerializer, SerializerMethodField

from crm.models import Customer, Contract, Event


class CustomerDetailSerializer(ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'compagny_name',
            'date_created',
            'date_updated',
            'existing',
            'notes',
            'seller',
            'id'
        ]


class CustomerListSerializer(ModelSerializer):
    
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'compagny_name',
            'existing',
            'id'
        ]


class ContractDetailSerializer(ModelSerializer):
    customer = SerializerMethodField()
    support = SerializerMethodField()
    event = SerializerMethodField()
    seller = SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'support',
            'seller',
            'customer',
            'event',
            'date_created',
            'date_updated',
            'signed',
            'date_signed',
            'due',
            'id'
        ]

    def get_customer(self, instance):
        return instance.customer.__str__()
    
    def get_support(self, instance):
        print(instance)
        return instance.support.__str__()
    
    def get_seller(self, instance):
        return instance.seller.__str__()
    
    def get_event(self, instance):
        return instance.event.__str__()


class ContractListSerializer(ModelSerializer):
    customer = SerializerMethodField()
    support = SerializerMethodField()
    event = SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'support',
            'customer',
            'event',
            'signed',
            'id'
        ]

    def get_customer(self, instance):
        return instance.customer.__str__()
    
    def get_support(self, instance):
        return instance.support.__str__()

    def get_event(self, instance):
        return instance.event.__str__()


class EventDetailSerializer(ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'name',
            'location',
            'date_created',
            'date_updated',
            'date_event',
            'finished',
            'id'
        ]


class EventListSerializer(ModelSerializer):
    
    class Meta:
        model = Event
        fields = [
            'name',
            'date_event',
            'id'
        ]
