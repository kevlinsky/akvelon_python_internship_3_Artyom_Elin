"""akvelonTestTask URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import *

schema_view = get_schema_view(
   openapi.Info(
      title="Akvelon Test Task service API",
      default_version='v1',
      description="API for manipulating with the users or their transactions",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'api'

urlpatterns = [
    # users
    path('user/create/', UserCreateAPIView.as_view(), name='create_user'),
    path('user/all/', UsersListAPIView.as_view(), name='all_users'),
    path('user/<int:pk>/', UserGetByIdAPIView.as_view(), name='get_user_by_id'),
    path('user/<str:email>/', UserGetByEmailAPIView.as_view(), name='get_user_by_email'),
    path('user/update/<int:pk>/', UserUpdateAPIView.as_view(), name='update_user'),
    path('user/delete/<int:pk>/', UserDeleteAPIView.as_view(), name='delete_user'),
    # user transactions
    path('user/<int:pk>/transactions/', UserTransactionsAPIView.as_view(), name='user_transactions'),
    path('user/<int:pk>/transactions/income/', UserIncomeTransactionsAPIView.as_view(), name='user_income_transactions'),
    path('user/<int:pk>/transactions/income/summary/', UserIncomeTransactionsSummaryAPIView.as_view(), name='user_income_transactions_summary'),
    path('user/<int:pk>/transactions/outcome/', UserOutcomeTransactionsAPIView.as_view(), name='user_outcome_transactions'),
    path('user/<int:pk>/transactions/outcome/summary/', UserOutcomeTransactionsSummaryAPIView.as_view(), name='user_outcome_transactions_summary'),
    # transactions
    path('transaction/create/', TransactionCreateAPIView.as_view(), name='create_transaction'),
    path('transaction/<int:pk>/', TransactionGetAPIView.as_view(), name='get_transaction'),
    path('transaction/update/<int:pk>/', TransactionsUpdateAPIView.as_view(), name='update_transaction'),
    path('transaction/delete/<int:pk>/', TransactionDeleteAPIView.as_view(), name='delete_transaction'),
    path('transaction/all/', TransactionsListAPIView.as_view(), name='all_transactions'),
    # tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # swagger
    re_path(r'^swagger(?:\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
