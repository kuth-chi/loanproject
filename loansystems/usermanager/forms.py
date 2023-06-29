from django.forms import ModelForm, SelectMultiple
from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files import  File
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class CollateralForm(ModelForm):
    class Meta:
        model = Collateral
        fields = '__all__'


class ImageCollateralForm(ModelForm):
    class Meta:
        model = ImageCollateral
        fields = '__all__'


class CountryForm(ModelForm):
    class Meta:
        model = Country
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput', 'placeholder': 'Enter country name', 'required': 'Please enter country name'}),
            'name_local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter local name', 'required': 'required'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short name'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter code'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency'}),
            'primary_language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter primary language'}),
            'alt_languages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'border_with': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter border with'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
            'landmark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter landmark'}),
            'leader_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter leader name'}),
            'leader_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter leader position'}),
            'born_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter born year'}),
            'is_before_chris': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if 'SA' in data:
            raise forms.ValidationError("Please Enter Country name")
        return data


class ProvinceForm(forms.ModelForm):
    country_id = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    ),

    class Meta:
        model = Province
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'enter province name', 'required': 'required'}),
            'name_local': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'name local'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short name'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency'}),
            'border_with': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter primary language'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'leader': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter border with'}),
            'hotline': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if 'SA' in data:
            raise forms.ValidationError("Please Enter Country name")
        return data


class DistrictForm(forms.ModelForm):
    province_id = forms.ModelMultipleChoiceField(
        queryset=Province.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    ),

    class Meta:
        model = District
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'enter district name', 'required': 'required'}),
            'name_local': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'name local'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short name'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency'}),
            'border_with': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter primary language'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'hotline': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if 'SA' in data:
            raise forms.ValidationError("Please Enter Country name")
        return data


class CommuneForm(forms.ModelForm):
    district_id = forms.ModelMultipleChoiceField(
        queryset=District.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    ),

    class Meta:
        model = Commune
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'enter commune name', 'required': 'required'}),
            'name_local': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'name local'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short name'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency'}),
            'border_with': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter primary language'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'hotline': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if 'SA' in data:
            raise forms.ValidationError("Please Enter Country name")
        return data


class VillageForm(forms.ModelForm):
    commune_id = forms.ModelMultipleChoiceField(
        queryset=District.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    ),

    class Meta:
        model = Village
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Enter commune name', 'required': 'required'}),
            'name_local': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Ente rname local'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short name'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency'}),
            'border_with': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter primary language'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'hotline': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        if 'SA' in data:
            raise forms.ValidationError("Please Enter Country name")
        return data


class CustomerFormAddress(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = '__all__'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class LoanDataForm(forms.ModelForm):
    CHOICES = (
        ('day', 'day'),
        ('week', 'week'),
        ('month', 'month'),
        ('quarter', 'quarter'),
        ('semester', 'semester'),
        ('year', 'year'),
    )
    RATE_CALCULATE_METHOD_CHOICES = (
        ('fixed flat', 'fixed flat'),
        ('Equal Installments', 'Equal Installments'),
        ('fixed rate', 'fixed rate'),
    )
    loan_cycle_type = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}), choices=CHOICES
    )
    rate_calculate_method = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}), choices=RATE_CALCULATE_METHOD_CHOICES
    )
    class Meta:
        model = Loan
        fields = ('loan_amount', 'loan_cycle_type', 'number_of_cycle',
                  'interest_rate_per_cycle', 'loan_date', 'is_set_first_payment_date',
                  'first_payment_date', 'rate_calculate_method', 'payment_schedule', 'full_off_from')
        widgets = {
            'loan_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '', 'required': 'required'}),
            'number_of_cycle': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'interest_rate_per_cycle': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'loan_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
            'border_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt languages'}),
            'first_payment_date': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter border length'}),
            'full_off_from': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter full pay off'}),
        }


class PaybackForm(forms.ModelForm):
    class Meta:
        model = Payback
        fields = '__all__'

        widgets = {
            'interest_paid': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'interest paid', 'required': 'required'}),
            'principle_paid': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'principle paid'}),
            'balance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Balance'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
        }


# =========================== ID CARD FORM ==================================

class IdCardForm(forms.ModelForm):

    class Meta:
        model = IdCard
        fields = '__all__'


class imageIdCardForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = imageIdCard
        fields = ('image_url', 'x', 'y', 'width', 'height')
        widgets = {
            'image_url': forms.FileInput(attrs={
                'accept': 'image/*'
            })
        }

    def save(self):
        photo = super(imageIdCard, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.file.path)

        return photo


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

class OwnerLogoForm(forms.ModelForm):
    class Meta:
        model = OwnerLogo
        fields = '__all__'
class CompanyAddressForm(forms.ModelForm):
    class Meta:
        model = CompanyAddress
        fields = '__all__'


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'

class CollateralFrom(forms.ModelForm):
    class Meta:
        model = Collateral
        fields = '__all__'

class ImageCollateral(forms.ModelForm):
    class Meta:
        model = ImageCollateral
        fields = '__all__'

class pawForm(forms.ModelForm):
    class Meta:
        model = Paw
        fields = '__all__'

class payPaw(forms.ModelForm):
    class Meta:
        model = PawPay
        fields = '__all__'
