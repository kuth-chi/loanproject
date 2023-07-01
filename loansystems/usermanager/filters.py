import django_filters
from .models import *
from django import forms, template
from django_filters import CharFilter


class CustomerFilter(django_filters.FilterSet):
    name = CharFilter(widget=forms.TextInput(
        attrs={"class": "form-control border-end-0 border rounded-pill", "placeholder": "search customer name",
               "max_length": "100"}))
    class Meta:
        model = Customer
        fields = ['name']


class loanSearchForm(django_filters.FilterSet):
    loan_number_id = CharFilter(widget=forms.TextInput(attrs={"class": "form-control border-end-0 border rounded-pill","placeholder": "search loan id", "max_length": "100"}))
    class Meta:
        model = Loan
        fields = ('loan_number_id',)

class LoanFilter(django_filters.FilterSet):
    class Meta:
        model = Loan
        fields = '__all__'

class ActivityFilter(django_filters.FilterSet):
    class Meta:
        model = Activity
        fields = '__all__'


class PaybackFilter(django_filters.FilterSet):
    class Meta:
        model = Payback
        fields = '__all__'
        exclude = ['attached_file']


class PawFilter(django_filters.FilterSet):
    class Meta:
        model = Paw
        fields = '__all__'
        exclude = ['paw_image']


class CustomerAddressFilter(django_filters.FilterSet):
    class Meta:
        model = CustomerAddress
        fields = '__all__'


class CollateralFilter(django_filters.FilterSet):
    class Meta:
        model = Collateral
        fields = '__all__'

class PositionFilter(django_filters.FilterSet):
    class Meta:
        model = Position
        fields = '__all__'

class DepartmentFilter(django_filters.FilterSet):
    class Meta:
        model = Department
        fields = '__all__'

