from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import AkvelonUser, Transaction
from .serializers import (UserSerializer,
                          UserGetSerializer,
                          TransactionSerializer,
                          TransactionCreateSerializer,
                          UserTransactionsSerializer,
                          UserIncomeTransactionsSummarySerializer,
                          UserOutcomeTransactionsSummarySerializer)
from .permissions import UpdatedPermission


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []
    queryset = AkvelonUser.objects.all()

    """
        Overridden post() method for catching read_only fields included in request
    """

    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields included in request',
        }
    )
    def post(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        return super(UserCreateAPIView, self).post(request, *args, **kwargs)


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [UpdatedPermission]
    queryset = AkvelonUser.objects.all()

    """
        Overridden patch() method for catching read_only fields included in request
    """

    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields or unknown fields included in request'
        }
    )
    def patch(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        return super(UserUpdateAPIView, self).patch(request, *args, **kwargs)

    """
        Overridden put() method for catching read_only fields included in request
    """

    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields or unknown fields included in request'
        }
    )
    def put(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        return super(UserUpdateAPIView, self).put(request, *args, **kwargs)

    """
        Overridden update() method for catching unknown model fields included in request
    """

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        for field in request.data:
            if field not in serializer.fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unknown field'})

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGetByIdAPIView(generics.RetrieveAPIView):
    serializer_class = UserGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = AkvelonUser.objects.all()
    lookup_field = 'pk'


"""
    API view for getting user by the email
"""


class UserGetByEmailAPIView(generics.RetrieveAPIView):
    serializer_class = UserGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = AkvelonUser.objects.all()
    lookup_field = 'email'
    lookup_url_kwarg = 'email'
    lookup_value_regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


class UserDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = AkvelonUser.objects.all()
    lookup_field = 'pk'


class UsersListAPIView(generics.ListAPIView):
    queryset = AkvelonUser.objects.all()
    serializer_class = UserGetSerializer
    permission_classes = [IsAuthenticated]
    # Two fields for providing users sorting by the first name, last name or both
    filter_backends = [OrderingFilter]
    ordering_fields = ['first_name', 'last_name']

    sort = openapi.Parameter('sort', openapi.IN_QUERY,
                             description="sort users by the <b>first_name</b>, <b>last_name</b> or <b>both</b>. Use '-' sign for reverse sorting",
                             type=openapi.TYPE_STRING,
                             required=False)

    @swagger_auto_schema(
        manual_parameters=[sort],
    )
    def get(self, request, *args, **kwargs):
        return super(UsersListAPIView, self).get(request, *args, **kwargs)


class UserTransactionsAPIView(generics.RetrieveAPIView):
    queryset = AkvelonUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserTransactionsSerializer
    lookup_field = 'pk'

    """
        Overridden get_queryset() method for filtering objects by the query parameters
    """

    def get_queryset(self):
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        prefetch = None
        if from_date is not None and to_date is not None:
            prefetch = Prefetch('transactions',
                                queryset=Transaction.objects.filter(date__gte=from_date, date__lte=to_date))
        if from_date is not None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(date__gte=from_date))
        if from_date is None and to_date is not None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(date__lte=to_date))
        if from_date is None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.all())
        return AkvelonUser.objects.prefetch_related(prefetch).all()

    from_date = openapi.Parameter('from_date', openapi.IN_QUERY,
                                  description="filter transactions starting from this date (e.g. 2021-05-15)",
                                  type=openapi.TYPE_STRING, required=False)
    to_date = openapi.Parameter('to_date', openapi.IN_QUERY,
                                description="filter transactions ending to this date (e.g. 2021-05-15)",
                                type=openapi.TYPE_STRING, required=False)

    @swagger_auto_schema(
        manual_parameters=[from_date, to_date],
    )
    def get(self, request, *args, **kwargs):
        return super(UserTransactionsAPIView, self).get(request, *args, **kwargs)


class UserIncomeTransactionsAPIView(generics.RetrieveAPIView):
    queryset = AkvelonUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserTransactionsSerializer
    lookup_field = 'pk'

    """
        Overridden get_queryset() method for filtering objects by the query parameters
    """

    def get_queryset(self):
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        prefetch = None
        if from_date is not None and to_date is not None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__gt=0, date__gte=from_date,
                                                                                    date__lte=to_date))
        if from_date is not None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__gt=0, date__gte=from_date))
        if from_date is None and to_date is not None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__gt=0, date__lte=to_date))
        if from_date is None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__gt=0))
        return AkvelonUser.objects.prefetch_related(prefetch).all()

    from_date = openapi.Parameter('from_date', openapi.IN_QUERY,
                                  description="filter transactions starting from this date (e.g. 2021-05-15)",
                                  type=openapi.TYPE_STRING, required=False)
    to_date = openapi.Parameter('to_date', openapi.IN_QUERY,
                                description="filter transactions ending to this date (e.g. 2021-05-15)",
                                type=openapi.TYPE_STRING, required=False)

    @swagger_auto_schema(
        manual_parameters=[from_date, to_date],
    )
    def get(self, request, *args, **kwargs):
        return super(UserIncomeTransactionsAPIView, self).get(request, *args, **kwargs)


class UserOutcomeTransactionsAPIView(generics.RetrieveAPIView):
    queryset = AkvelonUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserTransactionsSerializer
    lookup_field = 'pk'

    """
        Overridden get_queryset() method for filtering objects by the query parameters
    """

    def get_queryset(self):
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        prefetch = None
        if from_date is not None and to_date is not None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__lt=0, date__gte=from_date,
                                                                                    date__lte=to_date))
        if from_date is not None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__lt=0, date__gte=from_date))
        if from_date is None and to_date is not None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__lt=0, date__lte=to_date))
        if from_date is None and to_date is None:
            prefetch = Prefetch('transactions', queryset=Transaction.objects.filter(amount__lt=0))
        return AkvelonUser.objects.prefetch_related(prefetch).all()

    from_date = openapi.Parameter('from_date', openapi.IN_QUERY,
                                  description="filter transactions starting from this date (e.g. 2021-05-15)",
                                  type=openapi.TYPE_STRING, required=False)
    to_date = openapi.Parameter('to_date', openapi.IN_QUERY,
                                description="filter transactions ending to this date (e.g. 2021-05-15)",
                                type=openapi.TYPE_STRING, required=False)

    @swagger_auto_schema(
        manual_parameters=[from_date, to_date],
    )
    def get(self, request, *args, **kwargs):
        return super(UserOutcomeTransactionsAPIView, self).get(request, *args, **kwargs)


class UserIncomeTransactionsSummaryAPIView(generics.RetrieveAPIView):
    queryset = AkvelonUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserIncomeTransactionsSummarySerializer
    lookup_field = 'pk'


class UserOutcomeTransactionsSummaryAPIView(generics.RetrieveAPIView):
    queryset = AkvelonUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserOutcomeTransactionsSummarySerializer
    lookup_field = 'pk'


class TransactionCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionCreateSerializer

    """
        Overridden post() method for catching read_only fields included in request and
        resolving user by the id or email
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields or unknown fields included in request'
        }
    )
    def post(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        if 'user' in request.data:
            try:
                id = int(request.data['user'])
                request.data['user'] = id
            except ValueError:
                user = get_object_or_404(AkvelonUser, email=request.data['user'])
                id = user.id
                request.data['user'] = id
        return super(TransactionCreateAPIView, self).post(request, *args, **kwargs)


class TransactionGetAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_field = 'pk'


class TransactionsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Transaction.objects.all()

    """
        Overridden patch() method for catching read_only fields included in request and
        resolving user by the id or email
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields or unknown fields included in request'
        }
    )
    def patch(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        if 'user' in request.data:
            try:
                id = int(request.data['user'])
                request.data['user'] = id
            except ValueError:
                user = get_object_or_404(AkvelonUser, email=request.data['user'])
                id = user.id
                request.data['user'] = id
        return super(TransactionsUpdateAPIView, self).patch(request, *args, **kwargs)

    """
        Overridden patch() method for catching read_only fields included in request and
        resolving user by the id or email
    """
    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: 'Read only fields or unknown fields included in request'
        }
    )
    def put(self, request, *args, **kwargs):
        for field in request.data:
            if field in self.get_serializer().Meta.read_only_fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Read only field included'})
        if 'user' in request.data:
            try:
                id = int(request.data['user'])
                request.data['user'] = id
            except ValueError:
                user = get_object_or_404(AkvelonUser, email=request.data['user'])
                id = user.id
                request.data['user'] = id
        return super(TransactionsUpdateAPIView, self).put(request, *args, **kwargs)

    """
        Overridden update() method for catching unknown fields included in request
    """

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        for field in request.data:
            if field not in serializer.fields:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unknown field'})

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Transaction.objects.all()
    lookup_field = 'pk'


"""
    Custom Filter class for filtering transactions by the date
"""


class TransactionsDateFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name="date", lookup_expr='gte')
    to_date = filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['date']


class TransactionsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_class = TransactionsDateFilter
    # Two fields for providing transactions sorting by the date or amount
    # filter_backends = [OrderingFilter]
    ordering_fields = ['date', 'amount']

    """
        Overridden get_queryset() method for providing transactions filtering by the type (income / outcome)
    """

    def get_queryset(self):
        type = self.request.query_params.get('type')
        if type is not None:
            if type == 'income':
                return Transaction.objects.filter(amount__gt=0)
            elif type == 'outcome':
                return Transaction.objects.filter(amount__lt=0)
        return super(TransactionsListAPIView, self).get_queryset()

    from_date = openapi.Parameter('from_date', openapi.IN_QUERY,
                                  description="filter transactions starting from this date (e.g. 2021-05-15)",
                                  type=openapi.TYPE_STRING, required=False)
    to_date = openapi.Parameter('to_date', openapi.IN_QUERY,
                                description="filter transactions ending to this date (e.g. 2021-05-15)",
                                type=openapi.TYPE_STRING, required=False)
    type = openapi.Parameter('type', openapi.IN_QUERY,
                             description="type of the transaction: <b>income</b> or <b>outcome</b>",
                             type=openapi.TYPE_STRING,
                             required=False)
    sort = openapi.Parameter('sort', openapi.IN_QUERY,
                             description="sort transactions by the <b>date</b> or <b>amount</b>. Use '-' sign for reverse sorting",
                             type=openapi.TYPE_STRING,
                             required=False)

    @swagger_auto_schema(
        manual_parameters=[from_date, to_date, type, sort],
    )
    def get(self, request, *args, **kwargs):
        return super(TransactionsListAPIView, self).get(request, *args, **kwargs)
