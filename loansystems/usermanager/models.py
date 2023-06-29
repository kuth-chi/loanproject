import math
import os
import uuid

from django.core.files.base import ContentFile
from django.db import models
from datetime import date, timedelta, datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db.models.signals import pre_save  # new imported
from django.dispatch import receiver  # new imported
from decimal import Decimal, ROUND_HALF_UP  # new imported
from django.core.validators import MinValueValidator  # new imported
from django.contrib.postgres.fields import ArrayField  # to store array in a charfield
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
import random
import string
from django.utils.translation import gettext as _


def upload_customer_image(instance, filename):
    return "/".join(['image', str(instance), filename])


def upload_logo_company(instance, filename):
    return "/".join(['image', str(instance.name), filename])


def upload_logo_profile(instance, filename):
    return "/".join(['image', str('profile'), filename])


def upload_collateral_image(instance, filename):
    return "/".join(['image', str(instance), filename])


def owner_logo(instance, filename):
    return "/".join(['image', str(instance.user), filename])


def upload_id_image(instance, filename):
    return "/".join(['image', str(instance), filename])


class OwnerLogo(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=owner_logo, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


# FOR COMPANY / INDUSTRY
class Company(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    mr = models.BooleanField(blank=True, null=True, default=False)
    local_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to=upload_logo_company, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    tel_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    founded = models.DateField()
    founder = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    main_currency = models.CharField(max_length=3, blank=True, null=True, default='$')
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"  # for singular is Company with plural is companies

    def __str__(self):
        return f'{self.name} - {self.owner}'  # Show up company name on Admin list


# FOR COUNTRY DATABASE
class Country(models.Model):
    LEADER_POSITION_CHOICES = (
        ('Prime Minister', _('Prime Minister')),
        ('President', _('President')),
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    name_local = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=3, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    primary_language = models.CharField(max_length=50, blank=True, null=True)
    alt_languages = models.CharField(max_length=250, blank=True, null=True)
    border_with = models.CharField(max_length=250, blank=True, null=True)
    border_length = models.IntegerField(blank=True, null=True)
    landmark = models.IntegerField(blank=True, null=True)
    leader_name = models.CharField(max_length=100, blank=True, null=True)
    leader_position = models.CharField(max_length=100, blank=True, null=True)
    born_year = models.IntegerField(blank=True, null=True)
    is_before_chris = models.BooleanField(default=False, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = _('Countries')

    def __str__(self):
        return f'{self.name}'


class Province(models.Model):
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    name_local = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=3, blank=True, null=True)
    code = models.IntegerField()
    border_with = models.CharField(max_length=250, default=False, blank=True, null=True)
    border_length = models.IntegerField()
    leader = models.CharField(max_length=3, blank=True, null=True)
    hotline = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class District(models.Model):
    province_id = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True, )
    name = models.CharField(max_length=100, blank=True, null=True)
    name_local = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=3, blank=True, null=True)
    code = models.IntegerField()
    border_with = models.CharField(max_length=250, default=False, blank=True, null=True)
    border_length = models.IntegerField()
    hotline = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Commune(models.Model):
    district_id = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True, default=False)
    name = models.CharField(max_length=100, blank=True, null=True, default=False)
    name_local = models.CharField(max_length=100, blank=True, null=True, default=False)
    short_name = models.CharField(max_length=3, blank=True, null=True, default=False)
    code = models.IntegerField()
    border_with = models.CharField(max_length=250, default=False, blank=True, null=True)
    border_length = models.IntegerField()
    hotline = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Village(models.Model):
    commune_id = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True,
                                   default=False)  # Refer to Commune ID
    name = models.CharField(max_length=100, blank=True, null=True, default=False)
    name_local = models.CharField(max_length=100, blank=True, null=True, default=False)
    short_name = models.CharField(max_length=3, blank=True, null=True, default=False)
    code = models.IntegerField()
    border_with = models.CharField(max_length=250, default=False, blank=True, null=True)
    border_length = models.IntegerField()
    hotline = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


# FOR CUSTOMER.
class Customer(models.Model):
    name_kh = models.CharField(max_length=100, null=True, blank=True)
    customerId = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=200, null=True, default='Male')
    birthdate = models.DateField()
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    profile_img = models.ImageField(upload_to=upload_customer_image, null=True, blank=True)
    relationship_status = models.BooleanField(null=True, blank=True, )
    name_spouse = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_black_list = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True, )
    date_created = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.profile_img:
            # name_khmer = self.name_kh[0]
            name_english = self.name[0].upper()
            default_image = name_english
            size = (1024, 1024)
            bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
            img = Image.new("RGBA", size, bg_color)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 772)
            text_color = (255, 255, 255)
            text_color = text_color + (200,)
            text_width, text_height = draw.textsize(default_image, font=font)
            text_position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
            draw.text(text_position, default_image, text_color, font=font)
            img_file = BytesIO()
            img.save(img_file, format="PNG")
            self.profile_img.save(f"{self.name}_default.png", ContentFile(img_file.getvalue()), save=False)
        super().save(*args, **kwargs)


# CUSTOMER ADDRESS


class CustomerAddress(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, default=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True, default=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True, default=False)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True, default=False)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True, default=False)
    street = models.CharField(max_length=100, blank=True, null=True, default=False)
    house_number = models.CharField(max_length=100, blank=True, null=True, default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, default=False)
    location = models.CharField(max_length=50, blank=True, null=True, default=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = _('Customer Addresses')

    def __str__(self):
        return f"{self.customer.name}, {self.name}"


# CUSTOMER ADDRESS
class CustomerShippingAddress(models.Model):
    name: models.CharField(max_length=50, blank=True, null=True, default=False)
    country: models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True, default=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True, default=False)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True, default=False)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True, default=False)
    street = models.CharField(max_length=100, blank=True, null=True, default=False)
    house_number = models.CharField(max_length=100, blank=True, null=True, default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, default=False)
    location = models.CharField(max_length=50, blank=True, null=True, default=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = _('Customer Shipping Addresses')

    def __str__(self):
        return f"{self.customer.name}, {self.name}"


# COMPANY ADDRESS
class CompanyAddress(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True, default=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True, default=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True, default=False)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True, default=False)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True, default=False)
    street = models.CharField(max_length=100, blank=True, null=True, default=False)
    house_number = models.CharField(max_length=100, blank=True, null=True, default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, default=False)
    is_head_office = models.BooleanField(default=False, null=True, blank=True)
    location = models.CharField(max_length=50, blank=True, null=True, default=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = _('Company Addresses')

    def __str__(self):
        return f"{self.company.name}, {self.name}"


# =============================================================================
# =============================== NEW CODE ===== 01 - FEB - 2023 ==============
# =============================================================================
def generate_loan_id():
    """Generate a unique 8-character ID string for a loan."""
    while True:
        # Generate a random 8-character string using letters and digits
        random_chars = ''.join(random.choices(string.ascii_uppercase, k=4))
        random_digits = str(random.randint(1000, 9999))
        loan_number_id = random_digits + random_chars
        # Check if the loan ID is already in use
        if not Loan.objects.filter(loan_number_id=loan_number_id).exists():
            return loan_number_id


class Loan(models.Model):
    LOAN_CYCLE_TYPE_CHOICES = (
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
    STATUS = (
        ('on going', 'on going'),
        ('completed', 'completed'),
        ('lost', 'lost')
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_number_id = models.CharField(max_length=8, unique=True, null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    loan_cycle_type = models.CharField(max_length=8, choices=LOAN_CYCLE_TYPE_CHOICES)
    text_loan_amount = models.CharField(max_length=200, blank=True, null=True)
    number_of_cycle = models.PositiveIntegerField()
    interest_rate_per_cycle = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    loan_date = models.DateField()
    loan_status = models.CharField(max_length=20, blank=True, choices=STATUS, default='on going')
    full_off_from = models.BigIntegerField(blank=True, null=True, default=3)
    is_set_first_payment_date = models.BooleanField(default=False)
    first_payment_date = models.DateField(blank=True, null=True)
    rate_calculate_method = models.CharField(max_length=18, choices=RATE_CALCULATE_METHOD_CHOICES)
    payment_schedule = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.customer.name} (${self.loan_amount}) | {self.rate_calculate_method} | {self.first_payment_date}"

    def create_amortization_schedule(self):
        interest_rate = float((self.interest_rate_per_cycle) / 100)
        loan_amount = int(self.loan_amount)
        loan_type = self.loan_cycle_type
        loan_term = int(self.number_of_cycle)
        date_of_loan = self.loan_date
        set_payment_date = self.first_payment_date
        is_set_pay_date = self.is_set_first_payment_date
        # calculate the payment cycle based on loan_type
        if loan_type == 'day':
            payment_cycle = timedelta(days=1)
        elif loan_type == 'week':
            payment_cycle = timedelta(days=7)
        elif loan_type == 'month':
            payment_cycle = timedelta(days=30)
        elif loan_type == 'quarter':
            payment_cycle = timedelta(days=90)
        elif loan_type == 'semester':
            payment_cycle = timedelta(days=180)
        else:
            payment_cycle = timedelta(days=365)

        schedule = []
        if self.rate_calculate_method == 'fixed flat':
            fixed_payment = loan_amount / loan_term
            for i in range(0, loan_term + 1):
                if i == 0:
                    due_date = date_of_loan
                    principle = 0
                    interest = 0
                    loan_remaining = loan_amount
                elif i == 1 and not is_set_pay_date:
                    due_date = date_of_loan + payment_cycle
                    principle = fixed_payment
                    loan_remaining = loan_amount - principle
                    interest = loan_remaining * interest_rate
                elif i == 1 and is_set_pay_date:
                    # due_date = date_of_loan + (i-1)
                    due_date = set_payment_date + (i - 1) * payment_cycle
                    principle = fixed_payment
                    interest = loan_remaining * interest_rate
                    loan_remaining = loan_amount - principle
                else:  # if not set_pay_date and is_set_pay_date = false if not i == 0 and not i == 1
                    if set_payment_date:  # and set_payment_date != date_of_loan:
                        due_date = set_payment_date + (i - 1) * payment_cycle
                    else:
                        due_date = date_of_loan + (i * payment_cycle)

                    # due_date = date_of_loan + (i - 1) * (payment_cycle) #no need this because it's overridden
                    principle = fixed_payment
                    interest = loan_remaining * interest_rate
                    loan_remaining -= principle
                # monthly_payment = Decimal(loan_amount) / Decimal(loan_term)
                # principle = Decimal(monthly_payment).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                # loan_remaining = Decimal(loan_amount) - Decimal(principle)

                # check if due_date is on weekend and adjust accordingly
                if self.loan_cycle_type == "day":
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                    # interest = interest * number_of_days ## Calculate interest rate by day
                    monthly_interest = (interest) / \
                                       payment_cycle.days * number_of_days
                else:
                    if due_date.weekday() == 5:  # 5 is saturday
                        due_date += timedelta(days=2)
                    elif due_date.weekday() == 6:  # 6 is sunday
                        due_date += timedelta(days=1)
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                # interest = interest * number_of_days ## Calculate interest rate by day
                monthly_interest = (interest) / \
                                   payment_cycle.days * number_of_days
                schedule.append({
                    'number': i,
                    'due_date': due_date,
                    'number_date': number_of_days,
                    'interest': "{:.2f}".format(round(monthly_interest, 2)),
                    'principle': "{:.2f}".format(round(principle, 2)),
                    'monthly_amount': "{:.2f}".format(round(principle + monthly_interest, 2)),
                    'balance': "{:.2f}".format(round(loan_remaining, 2)),

                })

        # FIXED MONTLY PAYMENT ============================= NEED SOME UPDATE
        elif self.rate_calculate_method == 'Equal Installments':
            # if is_set_pay_date: # in case of loan set_pay_date the term will be longer.
            #     n = Decimal(((abs((date_of_loan - set_payment_date).days)) / payment_cycle.days) + loan_term)
            # else:
            # n = loan_term
            # Function for AMORTIZATION fixed MONTHLY PAYMENT
            monthly_amount = loan_amount / \
                             ((1 - (1 / (pow((1 + interest_rate), loan_term)))) / interest_rate)

            for i in range(0, loan_term + 1):
                monthly_payment = monthly_amount
                if i == 0:
                    due_date = date_of_loan
                    principle = 0
                    monthly_payment = monthly_payment * 0
                    loan_balance = loan_amount
                    interest_payment = 0
                elif i == 1 and not is_set_pay_date:  # DONE NO NEED TO EDIT THIS CODE
                    due_date = date_of_loan + timedelta(days=payment_cycle.days)
                    interest_payment = interest_rate * loan_amount  # interest in condition i == 1
                    principle = Decimal(monthly_payment) - \
                                Decimal(interest_payment)
                    # loan_amount -= Decimal(principle)
                    loan_balance -= principle

                elif i == 1 and is_set_pay_date:  # if i == 1 && Set_Pay_Date
                    due_date = set_payment_date + (i - 1) * payment_cycle
                    # + (schedule[i + loan_term - 2]['loan_balance']) # interest in condition i == 1 && set_payment_date
                    interest_payment = interest_rate * loan_amount
                    principle = Decimal(monthly_payment) - \
                                Decimal(interest_payment)
                    loan_balance -= principle  # Accumulate loan balance for each payment

                else:  # if not set_pay_date and is_set_pay_date = false if not i == 0 and not i == 1
                    if set_payment_date:
                        due_date = set_payment_date + (i - 1) * payment_cycle
                    else:
                        due_date = date_of_loan + (i) * payment_cycle

                    interest_payment = Decimal(loan_balance) * Decimal(interest_rate)  # not in conditions
                    principle = Decimal(monthly_payment) - \
                                Decimal(interest_payment)
                    loan_balance -= principle

                # check if due_date is on weekend and adjust accordingly
                if self.loan_cycle_type == "day":
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                    # interest = interest * number_of_days ## Calculate interest rate by day
                else:
                    if due_date.weekday() == 5:  # 5 is saturday
                        due_date += timedelta(days=2)
                    elif due_date.weekday() == 6:  # 6 is sunday
                        due_date += timedelta(days=1)
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                    # interest_payment = 1 #interest_rate * loan_amount # remove this to check condition
                    # principle = Decimal(monthly_payment) - Decimal(interest_payment)
                    # loan_balance -= Decimal(principle)
                schedule.append({
                    'number': i,
                    'due_date': due_date,
                    'number_date': number_of_days,
                    'interest': "{:.2f}".format(round(interest_payment, 2)),
                    'principle': "{:.2f}".format(round(principle, 2)),
                    'monthly_amount': "{:.2f}".format(round(monthly_payment, 2)),
                    'balance': "{:.2f}".format(round(loan_balance, 2)),
                })

        # FIXED RATE DONE NO NEED TO UPDATE
        else:  # Fixed Rate

            for i in range(0, loan_term + 1):
                if i == 0:
                    due_date = date_of_loan
                    principle = 0
                    interests = 0
                elif i == 1 and not is_set_pay_date:
                    due_date = date_of_loan + payment_cycle
                    principle = loan_amount / loan_term
                    interests = loan_amount * (interest_rate / payment_cycle.days)
                elif i == 1 and is_set_pay_date:
                    due_date = set_payment_date
                    principle = loan_amount / loan_term
                    interests = loan_amount * (interest_rate / payment_cycle.days)
                else:  # if not set_pay_date and is_set_pay_date = false
                    if set_payment_date:
                        due_date = set_payment_date + (i - 1) * payment_cycle
                    else:
                        due_date = date_of_loan + (i) * payment_cycle
                    principle = loan_amount / loan_term
                    interests = loan_amount * (interest_rate / payment_cycle.days)
                loan_remaining = loan_amount - (principle * (i))
                # monthly_amount = principle
                # check if due_date is on weekend and adjust accordingly
                if self.loan_cycle_type == "day":
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                    # interest = interest * number_of_days ## Calculate interest rate by day
                else:
                    if due_date.weekday() == 5:  # 5 is saturday
                        due_date += timedelta(days=2)
                    elif due_date.weekday() == 6:  # 6 is sunday
                        due_date += timedelta(days=1)
                    if i > 0:  # calculate number of day
                        prev_due_date = schedule[i - 1]['due_date']
                        number_of_days = abs((due_date - prev_due_date).days)
                    else:
                        number_of_days = 0
                interest = interests * number_of_days  # Calculate interest rate by day
                schedule.append({
                    'number': i,
                    'due_date': due_date,
                    'number_date': number_of_days,
                    'interest': "{:.2f}".format(round(interest, 2)),
                    'principle': "{:.2f}".format(round(principle, 2)),
                    'monthly_amount': "{:.2f}".format(round(principle + interest, 2)),
                    'balance': "{:.2f}".format(round(loan_remaining, 2)),
                })

        # schedule_instance = AmortizationSchedule(
        # loan_amount=loan_amount,
        # interest_rate=interest_rate,
        # loan_term=loan_term,
        # start_date=due_date,
        # schedule=schedule
        # )
        # schedule_instance.save()

        return schedule
        # self.payment_schedule = json.dumps(schedule)
        # self.save()   

    def save(self, *args, **kwargs):
        self.loan_number_id = generate_loan_id()
        super().save(*args, **kwargs)


def collateral_num():
    """Generate a unique 8-character ID string for a loan."""
    while True:
        # Generate a random 8-character string using letters and digits
        random_chars = ''.join(random.choices(string.ascii_uppercase, k=4))
        random_digits = str(random.randint(1000, 9999))
        collateral_num = random_digits + random_chars
        # Check if the loan ID is already in use
        if not Collateral.objects.filter(collateral_num=collateral_num).exists():
            return collateral_num


class Collateral(models.Model):
    status_col = (
        ("active", _('active')),
        ('refunded', _('refunded')),
        ('expired', _('expired')),
        ('sold', _('sold'))
    )
    cus_name = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)
    collateral_num = models.CharField(max_length=20, blank=True, unique=True)
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(max_length=200, null=True)
    condition = models.CharField(max_length=100, )
    price = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=8, choices=status_col)
    expired_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.collateral_num = collateral_num()
        super().save(*args, **kwargs)


# AUTOMATICALLY GENERATED SCHEDULE
class AmortizationSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    number = models.IntegerField()
    due_date = models.DateField()
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


# @receiver(pre_save, sender=Loan)
# def generate_amortization_schedule(sender, instance, **kwargs):
#     if not instance.pk:
#         instance.create_amortization_schedule()


# Payment Receipt Details
class LoanPaymentReceipt(models.Model):
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)
    pay_for_due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    pay_with = models.CharField(max_length=20)
    payer = models.CharField(max_length=20)
    is_penalty = models.BooleanField(default=False)
    number_of_day = models.PositiveIntegerField(blank=True, null=True)
    action_date = models.DateField()
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


class Payback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, blank=True, null=True)
    interest_paid = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    principle_paid = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    is_full_paid = models.BooleanField(default=False)
    full_paid = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    attached_file = models.ImageField(upload_to=upload_collateral_image, blank=True, null=True)
    due_date = models.DateField()
    pay_date = models.DateField()

    create_at = models.DateTimeField(auto_now=True)
    update_at = models.DateTimeField(auto_now=True)


# ============================================ Payback Image Instance and remove image data ===========


@receiver(models.signals.post_delete, sender=Payback)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleted file from filesystem
    when corresponding `ImageCollateral` object is deleted.
    """
    try:
        instance.attached_file.delete(save=False)
    except:
        pass


# OLD CODE #################################################################

# def generate_loan_id():
#     """Generate a unique 8-character ID string for a loan."""
#     while True:
#         # Generate a random 8-character string using letters and digits
#         random_chars = ''.join(random.choices(string.ascii_uppercase, k=4))
#         random_digits = str(random.randint(1000, 9999))
#         loan_number_id =  random_digits + random_chars
#         # Check if the loan ID is already in use
#         if not Loan.objects.filter(loan_number_id=loan_number_id).exists():
#             return loan_number_id


class ImageCollateral(models.Model):
    collateral = models.ForeignKey(Collateral, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=upload_collateral_image, blank=True, null=True)


class IdCard(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=120, blank=True)
    card_number = models.CharField(max_length=16, blank=True, )
    card_deadline = models.DateField(blank=True)


class imageIdCard(models.Model):
    id_card = models.ForeignKey(IdCard, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to=upload_id_image, blank=True, null=True)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)
    object = models.CharField(max_length=100)
    table = models.CharField(max_length=100, blank=True, null=True)
    update_on = models.CharField(max_length=100, blank=True, null=True)
    table_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    bank_account_name = models.CharField(max_length=50, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_account_currency = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)


class Paw(models.Model):
    status = (
        ("active", _('active')),
        ('refunded', _('refunded')),
        ('expired', _('expired')),
    )
    pay_method = (
        ("day", _('day')),
        ('week', _('week')),
        ('month', _('month')),
        ('year', _('year'))
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    paw_status = models.CharField(max_length=20, blank=True, choices=status, default='active')
    paw_pay_method = models.CharField(max_length=20, blank=True, choices=pay_method, default='day')
    paw_name = models.CharField(max_length=30, blank=True)
    paw_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True)
    paw_type = models.CharField(max_length=200, blank=True)
    is_percentage = models.BooleanField(default=False)
    rate = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, default=0)
    date_paw = models.DateField(blank=True, null=True)
    date_expired_paw = models.DateField(blank=True, null=True)
    paw_image = models.ImageField(upload_to=upload_customer_image, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


class PawBorrow(models.Model):
    paw = models.ForeignKey(Paw, on_delete=models.CASCADE)
    status = (
        ("active", _('active')),
        ('refunded', _('refunded')),
        ('expired', _('expired')),
    )
    pay_method = (
        ("day", _('day')),
        ('week', _('week')),
        ('month', _('month')),
        ('year', _('year'))
    )
    paw_borrow_status = models.CharField(max_length=20, blank=True, choices=status, default='active')
    paw_borrow_method = models.CharField(max_length=20, blank=True, choices=pay_method, default='day')
    paw_borrow_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    paw_borrow_type = models.CharField(max_length=200, blank=True)
    is_percentage = models.BooleanField(default=False)
    borrow_rate = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    is_principle = models.BooleanField(default=False, null=True)
    paw_borrow_principle_cycle = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    paw_borrow_period_principle = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    date_borrow = models.DateField(blank=True, null=True)
    date_expired_borrow = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True)


class Borrowpayback(models.Model):
    borrow = models.ForeignKey(PawBorrow, on_delete=models.CASCADE, null=True)
    pay_rate = models.DecimalField(max_digits=20, blank=True, default=0, decimal_places=2, null=True)
    pay_principle = models.DecimalField(max_digits=20, blank=True, default=0, decimal_places=2, null=True)
    total_pay = models.DecimalField(max_digits=20, blank=True, default=0, decimal_places=2, null=True)
    date_payback = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    update_date = models.DateTimeField(auto_now_add=True)


class pawImage(models.Model):
    paw = models.ForeignKey(Paw, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to=upload_customer_image, blank=True, null=True)
    crate_at = models.DateTimeField(auto_now_add=True)


class PawPay(models.Model):
    paw = models.ForeignKey(Paw, on_delete=models.CASCADE)
    pay_rate = models.DecimalField(max_digits=20, decimal_places=2, blank=True)
    pay_principle = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0)
    date_pay = models.DateField()
    remaining = models.DecimalField(max_digits=20, default=0, blank=True, decimal_places=2)
    attached_file = models.ImageField(upload_to=upload_collateral_image, blank=True)


class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    dep_name = models.CharField(max_length=150, blank=True)
    dep_desc = models.TextField(max_length=350, blank=True)
    created_at = models.DateField(auto_now=True, editable=True)
    update_at = models.DateField(auto_now=True, )

    def __str__(self):
        return self.dep_name

class Position(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    ps_name = models.CharField(max_length=150, blank=True)
    ps_desc = models.TextField(max_length=350, blank=True)
    created_at = models.DateField(auto_now=True, editable=True)
    update_at = models.DateField(auto_now=True, )

    def __str__(self):
        return self.ps_name


class EmployeeDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ImageField(upload_to=upload_logo_profile, default='static/img/profile_image_defautl.png')
    id_number = models.CharField(max_length=8, unique=True, editable=False)
    street = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    join_date = models.DateField(auto_now=True,)
    time_zone = models.CharField(max_length=128, default='UTC')
    created_at = models.DateField(auto_now=True, editable=True)
    update_at = models.DateField(auto_now=True, )

    def save(self, *args, **kwargs):
        self.id_number = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.first_name + self.last_name}'

# ========================================== ImageCollateral =================================
class EmployeeList(models.Model):
    emp_detail = models.ForeignKey(EmployeeDetail, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class Usersetting(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_sidebar = models.BooleanField(default=True)
# ================================ Customer Image data remove and update ====================================


# ======================== Collateral Image Instance and Remove Data ==================
@receiver(models.signals.post_delete, sender=ImageCollateral)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleted file from filesystem
    when corresponding `ImageCollateral` object is deleted.
    """
    try:
        instance.image.delete(save=False)
    except:
        pass


@receiver(models.signals.pre_save, sender=ImageCollateral)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        old_image = instance.__class__.objecs.get(id=instance.id).image.path
        try:
            new_image = instance.image.path
        except:
            new_image = None
        if new_image != old_image:
            import os
            if os.path.exists(old_image):
                os.remove(old_image)
    except:
        pass

class Investor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    value_invest = models.DecimalField(max_digits=20, blank=True, decimal_places=2)
    name_investor = models.CharField(max_length=30, blank=True)
    position_investor = models.CharField(max_length=20, blank=True)
    descriptions = models.TextField(blank=True)
    join = models.DateTimeField(blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

