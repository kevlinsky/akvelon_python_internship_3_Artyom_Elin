from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.db.models import Sum

from .models import AkvelonUser, Transaction

"""
    Serializer of the AkvelonUser model which are using to create or update AkvelonUser model
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvelonUser
        read_only_fields = (
            'id',
            'date_joined',
            'last_login',
            'is_admin',
            'is_active',
            'is_staff',
            'is_superuser',
        )
        fields = '__all__'

    """
        Overridden create method to provide hash of the input password instead of its raw value
    """
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    """
        Overridden update method to provide hash of the input password instead of its raw value
    """
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvelonUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'is_admin',
            'is_active',
            'is_staff',
            'is_superuser',
        )


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        read_only_fields = (
            'id',
            'date'
        )
        fields = (
            'id',
            'user',
            'date',
            'amount',
        )


class TransactionSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()

    class Meta:
        model = Transaction
        read_only_fields = (
            'id',
            'date'
        )
        fields = (
            'id',
            'user',
            'date',
            'amount',
        )


class TransactionsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        read_only_fields = (
            'id',
            'date'
        )
        fields = (
            'id',
            'date',
            'amount'
        )


class UserTransactionsSerializer(serializers.ModelSerializer):
    transactions = TransactionsListSerializer(many=True)

    class Meta:
        model = AkvelonUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'transactions'
        )


class UserIncomeTransactionsSummarySerializer(serializers.ModelSerializer):
    transactions_summary = serializers.SerializerMethodField('get_transactions_summary')

    """
        Serializer method for calculating the sum of the transactions grouped by date
    """
    def get_transactions_summary(self, user):
        return Transaction.objects.filter(user=user, amount__gt=0).values('date').annotate(sum=Sum('amount'))

    class Meta:
        model = AkvelonUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'transactions_summary'
        )


class UserOutcomeTransactionsSummarySerializer(serializers.ModelSerializer):
    transactions_summary = serializers.SerializerMethodField('get_transactions_summary')

    """
        Serializer method for calculating the sum of the transactions grouped by date
    """
    def get_transactions_summary(self, user):
        return Transaction.objects.filter(user=user, amount__lt=0).values('date').annotate(sum=Sum('amount'))

    class Meta:
        model = AkvelonUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'transactions_summary'
        )

