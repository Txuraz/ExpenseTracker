from django.db import models


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .models import Income, Expense
from .serializers import IncomeSerializer, ExpenseSerializer

# Create your models here.

class BalanceView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user_id = payload['user_id']

        # Calculate total income for the user
        total_income = Income.objects.filter(user_id=user_id).aggregate(total_income=models.Sum('amount'))['total_income'] or 0

        # Calculate total expense for the user
        total_expense = Expense.objects.filter(user_id=user_id).aggregate(total_expense=models.Sum('amount'))['total_expense'] or 0

        # Calculate the balance
        balance = total_income - total_expense

        return Response({'balance': balance})
