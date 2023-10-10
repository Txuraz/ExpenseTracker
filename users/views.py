from .models import User
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Income, Expense
from .serializers import IncomeSerializer, ExpenseSerializer
from django.db.models import Sum
from .serializers import UserSerializer


# Create your views here.
class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class Login(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.get(id=payload['id'])
        serializer = UserSerializer(user)
        return Response(serializer.data)


class Logout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message": "Logout successful"
        }
        return response


class IncomeListCreateView(generics.ListCreateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

    def perform_create(self, serializer):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            # Decode the JWT token using the 'secret' key
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        # Fetch the user associated with the JWT token's ID
        user_id = payload['id']
        user = User.objects.get(id=user_id)

        # Associate the income record with the authenticated user
        serializer.save(user=user)

    def list(self, request, *args, **kwargs):
        # This part lists income records for the authenticated user, similar to the 'ExpenseListCreateView'
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user_id = payload['id']
        incomes = Income.objects.filter(user_id=user_id)
        serializer = IncomeSerializer(incomes, many=True)
        return Response(serializer.data)


class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def perform_create(self, serializer):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user_id = payload['id']
        user = User.objects.get(id=user_id)
        serializer.save(user=user)

    def list(self, request, *args, **kwargs):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user_id = payload['id']
        expenses = Expense.objects.filter(user_id=user_id)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)


class BalanceView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.get(id=payload['id'])
        income_total = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = income_total - expense_total

        # Create a custom JSON response with total income, total expenses, and balance
        response_data = {
            'total_income': income_total,
            'total_expenses': expense_total,
            'balance': balance
        }

        return Response(response_data)


# views.py

class AllIncomeAndExpenseListView(generics.ListAPIView):
    serializer_class = IncomeSerializer

    def list(self, request, *args, **kwargs):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user_id = payload['id']

        # Retrieve all income and expense records for the authenticated user
        incomes = Income.objects.filter(user_id=user_id)
        expenses = Expense.objects.filter(user_id=user_id)

        income_serializer = IncomeSerializer(incomes, many=True)
        expense_serializer = ExpenseSerializer(expenses, many=True)

        # Merge the data from income and expense serializers
        merged_data = {
            'income': income_serializer.data,
            'expense': expense_serializer.data
        }

        return Response(merged_data)
