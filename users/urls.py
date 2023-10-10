from django.contrib import admin
from django.urls import path, include
from .views import Register, Login, UserView, Logout, IncomeListCreateView, ExpenseListCreateView, BalanceView, \
    AllIncomeAndExpenseListView

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('users', UserView.as_view()),
    path('logout', Logout.as_view()),
    path('income/', IncomeListCreateView.as_view(), name='income-list-create'),
    path('expense/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('balance/', BalanceView.as_view(), name='balance'),
    path('all/', AllIncomeAndExpenseListView.as_view(), name='all-income-expense'),
]