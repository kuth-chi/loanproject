import calendar
import decimal
import json

from django.shortcuts import render, redirect, get_object_or_404
# CHART JS
from django.views.generic import ListView

from .decorators import unautheticated_user, allowed_user, admin_only
from .models import *
from .forms import *
from django.contrib import messages
from django.forms import inlineformset_factory
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from .filters import *
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from uuid import UUID
from django.conf import settings
import socket, platform, os, uuid, re
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .paw_view import *
from django.utils.translation import get_language


# def restriction(request):
#     return render(request, 'accounts/user_restriction.html')

# ==================== view html ==========
@login_required(login_url='login')
def view_html_pdf(request, pk):
    loans = Loan.objects.get(id=pk)
    company_info = Company.objects.get(owner=request.user)
    id = company_info.id
    if Company.DoesNotExist:
        company_info = None
    customerId = Customer.objects.get(id=loans.customer_id)
    bankAccount = BankAccount.objects.filter(company=id)
    try:
        customerAddress = CustomerAddress.objects.get(customer=customerId.id)
    except CustomerAddress.DoesNotExist:
        customerAddress = None
    schedule = loans.create_amortization_schedule()
    total_interest = sum(Decimal(payment['interest']) for payment in schedule)
    total_day = sum(Decimal(payment['number_date']) for payment in schedule)
    total_principle = sum(Decimal(payment['principle']) for payment in schedule)
    total_in_loan = total_principle + total_interest
    context = {'loanList': loans, 'schedule': schedule,
               'customerId': customerId,
               'customerAddress': customerAddress,
               'total_in_loan': total_in_loan,
               'total_interest': total_interest,
               'total_principle': total_principle,
               'total_day': total_day,
               'company_info': company_info,
               'bankAccount': bankAccount
               }
    return render(request, 'dashboard/loan/report/preview_and_create_load_schedule.html', context)


# @login_required(login_url='login')

def view_function(request):
    user = request.user
    sidebar = Usersetting.objects.first()
    if request.user.is_authenticated:
        company = Company.objects.first()
        logo = OwnerLogo.objects.filter(user=user).order_by('-timestamp').first()
        # Check if a logo was found, otherwise use a default logo
        if not logo:
            logo = None
        return {'user': user, 'logo': logo, 'sidebar': sidebar, 'company': company, 'available_languages': ['en', 'km'],
                "lms_version": settings.VERSION, "release_date": settings.RELEASE}
    return {'available_languages': ['en', 'km']}


@unautheticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('/dashboard')
        else:
            messages.info(request, 'Username OR password is incorrect')
            return render(request, 'accounts/login.html')
    context = {}
    return render(request, 'accounts/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')


@unautheticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='employee')
            user.groups.add(group)
            messages.success(request, 'Account was created for' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


# ================== create company ===================
# @login_required(login_url='login')
content_type = ContentType.objects.get_for_model(Company)
company_permission = Permission.objects.filter(content_type=content_type)
def create_company(request, pk):
    if request.method == 'POST':
        name = request.POST['name']
        local_name = request.POST['local_name']
        logo = request.FILES['logo']
        vat_number = request.POST['vat_number']
        tel_number = request.POST['tel_number']
        email = request.POST['email']
        description = request.POST['description']
        founded = request.POST['founded']
        founder = request.POST['founder']
        Company_form = Company(name=name, local_name=local_name, logo=logo,
                               vat_number=vat_number, tel_number=tel_number,
                               email=email, description=description,
                               founded=founded, founder=founder,
                               owner=User.objects.get(id=pk))
        m = Company_form
        m.save()
        return redirect('/')
    return render(request, 'admin-company/company-form.html')


# =========================== create customer =====================
@login_required(login_url='login')
def update_customer(request, pk):
    updateCustomer = Customer.objects.get(id=pk)
    id = updateCustomer.id
    owner = request.user
    form = CustomerForm(instance=updateCustomer, )
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=updateCustomer, )
        if form.is_valid():
            form.save()
            messages.success(request, '.')
            return redirect('customer-detail', id)
    context = {'form': form, 'updateCustomer': updateCustomer}
    return render(request, 'dashboard/customer/customer_form.html', context)


# ====================== Customer list =============

@login_required(login_url='login')
@admin_only
def customer_list(request):
    listCustomer = Customer.objects.all().order_by('-id')
    customer_filter = CustomerFilter(request.GET, queryset=listCustomer)
    
    listCustomer = customer_filter.qs
    for customer in listCustomer:
        customer.total_loan_amount = Loan.objects.filter(customer=customer.id).aggregate(total_loan_amount=Sum('loan_amount'))['total_loan_amount']
    # customerAddress = CustomerAddress.objects.get()
    page = request.GET.get('page', 1)
    customers_data = []
    for i in listCustomer:
        id = i.id
        name = i.name
        name_kh = i.name_kh
        profile_img = i.profile_img
        email = i.email
        phone = i.phone
        relationship_status = i.relationship_status
        name_spouse = i.name_spouse
        is_black_list = i.is_black_list

        note = i.note
        try:
            idcard = IdCard.objects.get(customer=id)
            loan_counting = Loan.objects.filter(customer=i.id).count()
            customer_total_loan = Loan.objects.filter(customer=i.id).aggregate(total_loan_amount=Sum('loan_amount'))['total_loan_amount']
            paw_counting = Paw.objects.filter(customer=i.id).count()
            collateral_counting = Collateral.objects.filter(cus_name=i.id).count()
        except:
            idcard = 0
            loan_counting = 0
            paw_counting = 0
            collateral_counting = 0
            customer_total_loan = 0

        customers_data.append({
            'idcard': idcard,
            'id': id,
            'name': name,
            'name_kh': name_kh,
            'profile_img': profile_img,
            'email': email,
            'phone': phone,
            'relationship_status': relationship_status,
            'name_spouse': name_spouse,
            'is_black_list': is_black_list,
            'note': note,
            'loan_counting': loan_counting,
            'paw_counting': paw_counting,
            'collateral_counting': collateral_counting,
            'customer_total_loan': customer_total_loan,
        })

    paginator = Paginator(customers_data, 12)
    current_language = get_language()
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    context = {'customers': customers, 'paginator': paginator,
               'customers_data': customers_data,
               'customer_filter': customer_filter,
               'current_language': current_language
               }
    return render(request, 'dashboard/customer/list_customer.html', context)


# ======================== search customer =================

@login_required(login_url='login')
def search_customer(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        customerList = request.POST.get('customerList')
        query_customer = Customer.objects.filter(
            Q(name_kh__icontains=customerList) |
            Q(name__icontains=customerList) |
            Q(phone__icontains=customerList) |
            Q(email__icontains=customerList)
        )
        if len(query_customer) > 0 and len(customerList) > 0:
            customerData = []
            for i in query_customer:
                item = {
                    'id': i.id,
                    'name_kh': i.name_kh,
                    'name': i.name,
                    'phone': i.phone,
                    'email': i.email,
                    'profile_image': i.profile_img.url if i.profile_img else '',
                }
                customerData.append(item)
                res = customerData
        else:
            res = 'No customer name found with what name'
        return JsonResponse({'data': res})
    return JsonResponse({})


# =================== Test Search=================
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class customer_search_list(ListView):
    model = Customer
    template_name = 'dashboard/customer/list_customer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs_json"] = json.dumps(list(Customer.objects.values()), cls=UUIDEncoder)
        return context


@login_required(login_url='login')
def schedule_loan_json(request, pk):
    loan_id = Loan.objects.get(id=pk)
    schedule = loan_id.create_amortization_schedule()
    payback = Payback.objects.filter(loan=loan_id)
    return JsonResponse(schedule, safe=False)


# ========================= Customer ==================================
# ================================== detail customer
# ==================================  customer detail

@login_required(login_url='login')
# @allowed_user(allowed_roles=['employee'])
def customer_detail(request, pk):
    customer = Customer.objects.get(id=pk)
    today = datetime.today().date()
    month = today.month - 1
    year = today.year
    # ========================================= list loan customer =======================
    loanList = Loan.objects.filter(customer=customer.id).order_by('-id')
    paymentList = Payback.objects.filter(customer=customer.id).order_by('-id')
    pawList = Paw.objects.filter(customer=customer.id).order_by('-id')
    total_loan = sum(i.loan_amount for i in loanList)
    
    try:
        idCard = IdCard.objects.get(customer=pk)
        image_card = imageIdCard.objects.filter(id_card=idCard.id)
    except IdCard.DoesNotExist:
        idCard = None
        image_card = None

    # total_paw_payment = 0
    # Paw Payment list
    paw_pay_list = []
    for pPayment in pawList:
        paw_pay = PawPay.objects.filter(paw=pPayment.id)
        for i in paw_pay:
            paw_pay_list.append({
                'value_pay': i.pay_value
            })
    # Total all payment  
    total_payback = sum(i.balance for i in paymentList) + sum(i.full_paid for i in paymentList) + sum(
        i['value_pay'] for i in paw_pay_list)

    # ================================= filter over due data in loan list =================
    detail_loan = []

    for loan in loanList:
        id = loan.id
        loan_number_id = loan.loan_number_id
        loan_amount = loan.loan_amount
        loan_date = loan.loan_date
        loan_cycle_type = loan.loan_cycle_type
        number_of_cycle = loan.number_of_cycle
        interest_rate_per_cycle = loan.interest_rate_per_cycle
        loan_status = loan.loan_status
        full_off_from = loan.full_off_from
        rate_calculate_method = loan.rate_calculate_method

        over_due = loan.create_amortization_schedule()

        count_schedule = len(over_due) - 1
        del over_due[0]
        over_due_date = []
        have_paid = []
        have_paid_due = []
        for i in over_due:
            due_date = i['due_date']
            monthly_amount = i['monthly_amount']
            id = loan.id
            if due_date < today:
                over_due_date.append({
                    'over_due': 0,
                    'balance': Decimal(monthly_amount),
                    'due_date': due_date
                })

            for pay in paymentList:
                if due_date == pay.due_date and pay.balance == Decimal(monthly_amount):
                    have_paid.append({
                        'over_due': 0,
                        'overdate': pay.due_date,
                        'balance': pay.balance,
                        'full_paid': pay.full_paid
                    })
                if due_date == pay.due_date < today:
                    have_paid_due.append({
                        'over_due': 0,
                        'overdate': pay.due_date,
                        'balance': pay.balance,
                    })
        count_over_due = sum('over_due' in i for i in over_due_date) - sum('over_due' in i for i in have_paid)
        total_over_due = sum(i['balance'] for i in over_due_date)
        number_paid = sum('balance' in i for i in have_paid)
        sum_over_due = sum(Decimal(i['balance']) for i in over_due_date) - sum(i['balance'] for i in have_paid_due)
        if count_over_due < 0:
            count_over_due = 0
        else:
            count_over_due = sum('over_due' in i for i in over_due_date) - sum('over_due' in i for i in have_paid)
        detail_loan.append({
            'id': id,
            'loan_number_id': loan_number_id,
            'number_of_cycle': number_of_cycle,
            'loan_amount': loan_amount,
            'loan_date': loan_date,
            'loan_cycle_type': loan_cycle_type,
            'interest_rate_per_cycle': interest_rate_per_cycle,
            'loan_status': loan_status,
            'full_off_from': full_off_from,
            'rate_calculate_method': rate_calculate_method,
            'count_over_due': count_over_due,
            'have_paid': number_paid,
            'count_schedule': count_schedule,
            'total_over_due': total_over_due,
            'sum_over_due': sum_over_due,
            
        })

        # ============================== chart customer detail ===========================

    this_year_payback = []
    current_year = today.year

    for month in range(1, 13):
        name = calendar.month_name[month]
        balance_year = Payback.objects.filter(customer=pk, due_date__year=current_year, due_date__month=month).values(
            'balance')
        fd_year = Payback.objects.filter(customer=pk, due_date__year=current_year, due_date__month=month).values(
            'full_paid')
        sum_fd_year = sum(pay['full_paid'] for pay in fd_year)
        sum_balance_year = sum(pay['balance'] for pay in balance_year)
        sum_this_year = sum_balance_year + sum_fd_year
        this_year_payback.append({
            'payback': sum_balance_year,
            'paybackFullPaid': sum_fd_year,
            'name': name,
        })
    try:
        idCard = IdCard.objects.get(customer=pk)
        image_idCard = imageIdCard.objects.filter(id_card=idCard.id)
    except IdCard.DoesNotExist:
        idCard = False
        image_idCard = False

    customerAddress = CustomerAddress.objects.filter(customer_id=customer.id)
    if request.method == "POST":
        customer.delete()
        activity = Activity(
            user=request.user,
            action='delete',
            object='on ' + customer,
            update_on='',
            table='customer',
            table_id=customer.id
        )
        activity.save()
        return redirect('/customer')

    filterCollateral = Collateral.objects.filter(cus_name=customer.id).order_by('-id')
    collateralList = []
    for i in filterCollateral:
        id = i.id
        title = i.title
        condition = i.condition
        status = i.status
        price = i.price
        date = i.date
        expired_date = i.expired_date
        filterImagecollateral = ImageCollateral.objects.filter(collateral=i.id)
        image = ''
        for j in filterImagecollateral:
            image = j.image
        collateralList.append({
            'id': id,
            'title': title,
            'condition': condition,
            'status': status,
            'price': price,
            'date': date,
            'expired_date': expired_date,
            'image': image

        })
    total_over_due_all = sum(i['sum_over_due'] for i in detail_loan)
    current_language = get_language()
    context = {'customerDetail': customer,
               'image_card': image_card,
               'idCard': idCard,
               'this_year_payback': this_year_payback,
               'image_idCard': image_idCard,
               'loanList': loanList,
               'item': customer,
               'total_loan': total_loan,
               'paymentList': paymentList,
               'collateralList': collateralList,
               'total_payback': total_payback,
               'detail_loan': detail_loan,
               'total_over_due_all': total_over_due_all,
               'pawList': pawList,
               'customerAddress': customerAddress,
               'current_language': current_language,
               }
    return render(request, 'dashboard/customer/customer_detail.html', context)


# create customer
@login_required(login_url='login')
def create_customer(request):
    # form = CustomerForm
    customerList = Customer.objects.all()
    if request.method == 'POST':
        name_kh = request.POST['name_kh']
        name = request.POST['name']
        gender = request.POST['gender']
        birthdate = request.POST['birthdate']
        email = request.POST['email']
        phone = request.POST['phone']
        if 'profile_img' in request.FILES:
            profile_img = request.FILES['profile_img']
        else:
            profile_img = None

        status = request.POST.get('relationship_status')
        if status == 'on':
            relationship_status = True
        else:
            relationship_status = False
        Customer_form = Customer(name_kh=name_kh, name=name, gender=gender,
                                 birthdate=birthdate, email=email, phone=phone, profile_img=profile_img,
                                 relationship_status=relationship_status, )
        m = Customer_form
        m.save()
        activity = Activity(user=request.user, action='create new', object=name,
                            table='customer', table_id=m.id)
        activity.save()
        messages.success(request, 'Create customer successfully')
        return redirect('customer')
    context = {'customerList': customerList}
    return render(request, 'dashboard/customer/customer_form.html', context)


# update customer
@login_required(login_url='login')
def update_customer(request, pk):
    updateCustomer = Customer.objects.get(id=pk)
    id = updateCustomer.id
    context = {'updateCustomer': updateCustomer}
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        status = request.POST.get('relationship_status')
        if status == 'on':
            relationship_status = True
        else:
            relationship_status = False
        form = CustomerForm(request.POST, request.FILES, instance=updateCustomer)
        if form.is_valid():
            form = form.save(commit=False)
            form.customer = Customer.objects.get(id=pk)
            form.relationship_status = relationship_status
            form.email = email
            activity = Activity(
                user=request.user,
                action='update',
                object=name,
                update_on=updateCustomer.name,
                table='customer',
                table_id=id
            )
            activity.save()
            form.save()
            messages.success(request, 'Update customer successfully!')
            return redirect('update_customer', id)
        else:
            messages.error(request, 'Update customer failed')
        return render(request, 'dashboard/customer/customer_form.html', context)
    else:
        return render(request, 'dashboard/customer/customer_form.html', context)


# delete customer
@login_required(login_url='login')
def delete_customer(request, pk):
    customer = Customer.objects.get(id=pk)
    if request.method == "POST":
        customer.delete()
        activity = Activity(
            user=request.user,
            action='delete',
            object=customer.name,
            update_on=customer.name,
            table='customer',
            table_id=customer.id
        )
        activity.save()
        return redirect('/customer')
    context = {'item': customer}
    return render(request, 'dashboard/customer/delete.html', context)


# ========================= customer Address ================================
@login_required(login_url='login')
def address(request):
    customerAddress = CustomerAddress.objects.all().order_by('-id')
    address_filter = CustomerAddressFilter(request.GET, queryset=customerAddress)
    addressData = address_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(addressData, 9)
    try:
        addressData = paginator.page(page)
    except PageNotAnInteger:
        addressData = paginator.page(1)
    except EmptyPage:
        addressData = paginator.page(paginator.num_pages)
    context = {'customerAddress': customerAddress, 'addressData': addressData, 'paginator': paginator}
    return render(request, 'dashboard/address/base_address.html', context)


# ================================= search address ===================
def search_customerAddress(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        addressList = request.POST.get('addressList')
        query_address = CustomerAddress.objects.filter(
            Q(customer__name_kh__icontains=addressList) |
            Q(customer__name__icontains=addressList) |
            Q(country__name__icontains=addressList) |
            Q(country__name_local__icontains=addressList) |
            Q(province__name__icontains=addressList) |
            Q(province__name_local__icontains=addressList) |
            Q(commune__name_local__icontains=addressList) |
            Q(commune__name__icontains=addressList) |
            Q(district__name__icontains=addressList) |
            Q(district__name_local__icontains=addressList) |
            Q(village__name__icontains=addressList) |
            Q(village__name_local__icontains=addressList)
        )

        if len(query_address) > 0 and len(addressList) > 0:
            data = []
            for i in query_address:
                item = {
                    'id': i.customer.id,
                    'name': i.customer.name,
                    'name_kh': i.customer.name_kh,
                    'country': i.country.name_local,
                    'province': i.province.name_local,
                }
                data.append(item)
            res = data
        else:
            res = 'No customer address found with what name'
        return JsonResponse({'data': res})


# ========================= County ================================
# create country
@login_required(login_url='login')
def create_county(request):
    country = Country.objects.all()
    form = CountryForm()
    if request.method == 'POST':
        country = request.POST['name']
        form = CountryForm(request.POST)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object=country,
                update_on=country,
                table='country',
                table_id=m.id
            )
            activity.save()
            return redirect('country_list')
    context = {'country': country, 'form': form}
    return render(request, 'dashboard/address/country/country_form.html', context)


# country list


@login_required(login_url='login')
def country_list(request):
    country = Country.objects.all().order_by('-id')
    context = {'countrylist': country}
    return render(request, 'dashboard/address/country/country_list.html', context)


# country detail


@login_required(login_url='login')
def country_detail(request, pk):
    countryDetail = Country.objects.get(id=pk)
    context = {'countryDetail': countryDetail}
    if request.method == "POST":
        countryDetail.delete()
        return redirect('country_list')
    return render(request, 'dashboard/address/country/country_detail.html', context)


# update country


@login_required(login_url='login')
def update_country(request, pk):
    country = Country.objects.get(id=pk)
    form = CountryForm(instance=country)

    countryID = country.id
    if request.method == 'POST':
        name = request.POST['name']
        form = CountryForm(request.POST or None, instance=country)
        if form.is_valid():
            activity = Activity(
                user=request.user,
                action='update',
                object=country.name,
                update_on=name,
                table='country',
                table_id=countryID
            )
            activity.save()
            form.save()
            return redirect('country_detail', countryID)
    context = {'form': form, 'countryID': countryID}
    return render(request, 'dashboard/address/country/country_form.html', context)

    # Delete country


@login_required(login_url='login')
def delete_country(request, pk):
    country = Country.objects.get(id=pk)
    if request.method == "POST":
        country.delete()
        activity = Activity(
            user=request.user,
            action='delete',
            object=country.name,
            update_on='',
            table='country',
            table_id=country.id
        )
        activity.save()
        return redirect('country_list')
    context = {'item': country}
    return render(request, 'dashboard/address/country/country_detail.html', context)


# ==================== province =========================


@login_required(login_url='login')
def province_list(request):
    province = Province.objects.all().order_by('-id')
    context = {'provinceList': province}
    return render(request, 'dashboard/address/province/province_list.html', context)


# ================== create province ============================


@login_required(login_url='login')
def create_province(request):
    province = Province.objects.all()
    form = ProvinceForm()
    if request.method == 'POST':
        form = ProvinceForm(request.POST)
        name = request.POST['name']
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object=name,
                update_on='',
                table='province',
                table_id=m.id
            )
            activity.save()
            return redirect('province_list')
        else:
            form = ProvinceForm()
    context = {'province': province, 'form': form}
    return render(request, 'dashboard/address/province/province_form.html', context)


# ========================= detail province ============================


@login_required(login_url='login')
def province_detail(request, pk):
    provinceDetail = Province.objects.get(id=pk)
    context = {'provinceDetail': provinceDetail}
    if request.method == "POST":
        provinceDetail.delete()
        return redirect('province_list')
    return render(request, 'dashboard/address/province/province_detail.html', context)


# ====================== update ======================


@login_required(login_url='login')
def update_province(request, pk):
    province = Province.objects.get(id=pk)
    form = ProvinceForm(instance=province)
    provinceID = province.id
    if request.method == 'POST':
        name = request.POST['name']
        form = CountryForm(request.POST or None, instance=province)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='update',
                object=name,
                update_on='',
                table='province',
                table_id=m.id
            )
            activity.save()
            return redirect('province_detail', provinceID)
    context = {'form': form, 'provinceID': provinceID}
    return render(request, 'dashboard/address/province/province_form.html', context)


# =============== delete province ================


@login_required(login_url='login')
def delete_province(request, pk):
    province = Province.objects.get(id=pk)
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=province.name,
            update_on='',
            table='province',
            table_id=''
        )
        activity.save()
        province.delete()
        return redirect('province_list')
    context = {'item': province}
    return render(request, 'dashboard/address/province/province_detail.html', context)


# ============================= district ================


@login_required(login_url='login')
def district_list(request):
    district = District.objects.all().order_by('-id')
    context = {'districtList': district}
    return render(request, 'dashboard/address/district/district_list.html', context)


# =============================  create district ======================


@login_required(login_url='login')
def create_district(request):
    district = District.objects.all()
    form = DistrictForm()
    if request.method == 'POST':
        name = request.POST['name']
        form = DistrictForm(request.POST)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object=name,
                update_on='',
                table='district',
                table_id=m.id
            )
            activity.save()
            return redirect('district_list')
        else:
            form = ProvinceForm()
    context = {'district': district, 'form': form}
    return render(request, 'dashboard/address/district/district_form.html', context)


# ==================== district detail =================


@login_required(login_url='login')
def district_detail(request, pk):
    districtDetail = District.objects.get(id=pk)
    context = {'districtDetail': districtDetail}
    if request.method == "POST":
        districtDetail.delete()
        return redirect('province_list')
    return render(request, 'dashboard/address/district/district_detail.html', context)


# ================ update district ===============


@login_required(login_url='login')
def update_district(request, pk):
    district = District.objects.get(id=pk)
    form = DistrictForm(instance=district)
    districtID = district.id
    if request.method == 'POST':

        form = CountryForm(request.POST or None, instance=district)
        if form.is_valid():
            activity = Activity(
                user=request.user,
                action='update',
                object=district.name,
                update_on='',
                table='district',
                table_id=district.id
            )
            activity.save()
            form.save()
            return redirect('district_detail', districtID)
    context = {'form': form, 'districtID': district}
    return render(request, 'dashboard/address/district/district_form.html', context)


# ========== delete district ==================


@login_required(login_url='login')
def delete_district(request, pk):
    district = District.objects.get(id=pk)
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=district.name,
            update_on='',
            table='district',
            table_id=district.id
        )
        activity.save()
        district.delete()
        return redirect('district_list')
    context = {'item': district}
    return render(request, 'dashboard/address/district/district_detail.html', context)


# ========== list commune ==================


@login_required(login_url='login')
def commune_list(request):
    commune = Commune.objects.all().order_by('-id')
    context = {'communeList': commune}
    return render(request, 'dashboard/address/commune/commune_list.html', context)


# ========== create commune ==================


@login_required(login_url='login')
def create_commune(request):
    commune = Commune.objects.all()
    form = CommuneForm()
    if request.method == 'POST':
        name = request.POST['name']
        form = CommuneForm(request.POST)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object=name,
                update_on='',
                table='commune',
                table_id=m.id
            )
            activity.save()
            return redirect('commune_list')
        else:
            form = ProvinceForm()
    context = {'commune': commune, 'form': form}
    return render(request, 'dashboard/address/commune/commune_form.html', context)


# ========== commune detail ==================


@login_required(login_url='login')
def commune_detail(request, pk):
    communeDetail = Commune.objects.get(id=pk)
    context = {'communeDetail': communeDetail}
    if request.method == "POST":
        communeDetail.delete()
        activity = Activity(
            user=request.user,
            action='delete',
            object=communeDetail.name,
            update_on='',
            table='commune',
            table_id=communeDetail.id
        )
        activity.save()
        return redirect('commune_list')
    return render(request, 'dashboard/address/commune/commune_detail.html', context)


# ===================== commune update ==================
@login_required(login_url='login')
def update_commune(request, pk):
    communeDetail = Commune.objects.get(id=pk)
    form = CommuneForm(instance=communeDetail)
    communeID = communeDetail.id
    if request.method == 'POST':
        form = CommuneForm(request.POST or None, instance=communeDetail)
        if form.is_valid():
            form.save()
            activity = Activity(
                user=request.user,
                action='update',
                object=communeDetail.name,
                update_on='',
                table='commune',
                table_id=communeDetail.id
            )
            activity.save()
            return redirect('commune_detail', communeID)
    context = {'form': form, 'communeID': communeDetail}
    return render(request, 'dashboard/address/commune/commune_form.html', context)


# ===================== commune delete ===================


@login_required(login_url='login')
def delete_commune(request, pk):
    commune = Commune.objects.get(id=pk)
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=commune.name,
            update_on='',
            table='commune',
            table_id=commune.id
        )
        activity.save()
        commune.delete()
        return redirect('commune_list')
    context = {'item': commune}
    return render(request, 'dashboard/address/commune/commune_detail.html', context)


# =========== village list ==================
@login_required(login_url='login')
def village_list(request):
    village = Village.objects.all().order_by('-id')
    context = {'villageList': village}
    return render(request, 'dashboard/address/village/village_list.html', context)


# =========================== create village ====================

@login_required(login_url='login')
def create_village(request):
    village = Village.objects.all()
    form = VillageForm()
    if request.method == 'POST':
        name = request.POST['name']
        form = VillageForm(request.POST)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object=name,
                update_on='',
                table='village',
                table_id=m.id
            )
            activity.save()
            return redirect('village_list')
        else:
            form = ProvinceForm()
    context = {'village': village, 'form': form}
    return render(request, 'dashboard/address/village/village_form.html', context)


# =============== village detail ====================


@login_required(login_url='login')
def village_detail(request, pk):
    villageDetail = Village.objects.get(id=pk)
    context = {'villageDetail': villageDetail}
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=villageDetail.name,
            update_on='',
            table='village',
            table_id=villageDetail.id
        )
        activity.save()
        villageDetail.delete()
        return redirect('village_list')
    return render(request, 'dashboard/address/village/village_detail.html', context)


# ====================== village update =========================


@login_required(login_url='login')
def update_village(request, pk):
    village = Village.objects.get(id=pk)
    form = VillageForm(instance=village)
    villageID = village.id
    if request.method == 'POST':
        form = VillageForm(request.POST or None, instance=village)
        if form.is_valid():
            activity = Activity(
                user=request.user,
                action='update',
                object=village.name,
                update_on='',
                table='village',
                table_id=village.id
            )
            activity.save()
            form.save()
            return redirect('village_detail', villageID)
    context = {'form': form, 'villageID': village}
    return render(request, 'dashboard/address/village/village_form.html', context)


# ======================= delete village =========================


@login_required(login_url='login')
def delete_village(request, pk):
    village = Village.objects.get(id=pk)
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=village.name,
            update_on='',
            table='village',
            table_id=village.id
        )
        activity.save()
        village.delete()
        return redirect('village_list')
    context = {'item': village}
    return render(request, 'dashboard/address/village/village_detail.html', context)


# ===================== create customer address =====================
@login_required(login_url='login')
def create_customer_address(request, pk):
    customerId = Customer.objects.get(id=pk)
    countryList = Country.objects.all().order_by('-id')
    provinceList = Province.objects.all().order_by('-id')
    districtList = District.objects.all().order_by('-id')
    communeList = Commune.objects.all().order_by('-id')
    villageList = Village.objects.all().order_by('-id')
    if request.method == 'POST':
        name = request.POST['name']
        country_id = request.POST['country']
        country = Country.objects.get(id=country_id)
        province_id = request.POST['province']
        province = Province.objects.get(id=province_id)
        district_id = request.POST['district']
        district = District.objects.get(id=district_id)
        commune_id = request.POST['commune']
        commune = Commune.objects.get(id=commune_id)
        village_id = request.POST['village']
        village = Village.objects.get(id=village_id)
        street = request.POST['street']
        house_number = request.POST['house_number']
        location = request.POST['location']
        customerAddressForm = CustomerAddress(
            name=name, country=country,
            province=province, district=district,
            commune=commune, village=village,
            street=street, house_number=house_number,
            customer=customerId, location=location
        )
        m = customerAddressForm
        m.save()
        activity = Activity(
            user=request.user,
            action='create new',
            object=name,
            update_on='',
            table='customer address',
            table_id=m.id
        )
        activity.save()
        messages.success(request, 'Add address for customer' + customerId.name)
        return redirect('customer-detail', customerId.id)
    context = {'customerId': customerId, 'countryList': countryList,
               'provinceList': provinceList, 'districtList': districtList,
               'communeList': communeList, 'villageList': villageList}
    return render(request, 'dashboard/customer/cus_address/customer_address_form.html', context)


# ================= update customer address =================


@login_required(login_url='login')
def update_customer_address(request, pk):
    customerAddressId = CustomerAddress.objects.get(id=pk)
    customer = Customer.objects.get(id=customerAddressId.customer.id)
    customerId = customer.id
    countryList = Country.objects.all().order_by('-id')
    provinceList = Province.objects.all().order_by('-id')
    districtList = District.objects.all().order_by('-id')
    communeList = Commune.objects.all().order_by('-id')
    villageList = Village.objects.all().order_by('-id')
    if request.method == 'POST':
        form = CustomerFormAddress(
            request.POST or None, instance=customerAddressId)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='update',
                object=customer.name,
                update_on='',
                table='customer address',
                table_id=m.id
            )
            activity.save()
            return redirect('customer-detail', customerId)
    context = {'customerAddressId': customerAddressId, 'countryList': countryList,
               'provinceList': provinceList, 'districtList': districtList,
               'communeList': communeList, 'villageList': villageList}
    return render(request, 'dashboard/customer/cus_address/customer_address_form.html', context)


# ================= delete customer address =================

@login_required(login_url='login')
def delete_customer_address(request, pk):
    customerAddressId = CustomerAddress.objects.get(id=pk)
    if request.method == "POST":
        activity = Activity(
            user=request.user,
            action='delete',
            object=customerAddressId.name,
            update_on='',
            table='customer address',
            table_id=customerAddressId.id
        )
        activity.save()
        customerAddressId.delete()
        return redirect('customer-detail', customerAddressId.customer.id)
    context = {'item': customerAddressId}
    return render(request, 'dashboard/customer/cus_address/customer_address_form.html', context)


# ================================= search collateral ===================

def search_collateral(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        collateralList = request.POST.get('collateralList')
        query_collateral = Collateral.objects.filter(
            Q(cus_name__name_kh__icontains=collateralList) |
            Q(cus_name__name__icontains=collateralList) |
            Q(description__icontains=collateralList) |
            Q(condition__icontains=collateralList) |
            Q(price__icontains=collateralList)
        )

        if len(query_collateral) > 0 and len(collateralList) > 0:
            data = []
            for i in query_collateral:
                item = {
                    'id': i.id,
                    'name': i.cus_name.name,
                    'name_kh': i.cus_name.name_kh,
                    'title': i.title,
                }
                data.append(item)
            res = data
        else:
            res = 'No customer address found with what name'
        return JsonResponse({'data': res})


# ================= collateral detail =================


@login_required(login_url='login')
def collateral_detail(request, pk):
    user = request.user
    today = date.today()
    month = date.today().month
    collateralDetail = Collateral.objects.get(id=pk)
    customer_id = collateralDetail.cus_name

    loan_id = collateralDetail.loan
    try:
        customerAddress = CustomerAddress.objects.get(customer=customer_id)
    except CustomerAddress.DoesNotExist:
        customerAddress = 0
    try:

        customerIdCard = IdCard.objects.get(customer=customer_id)
    except IdCard.DoesNotExist:
        customerIdCard = 0

    try:
        schedule = loan_id.create_amortization_schedule()
    except Loan.DoesNotExist:
        schedule = False
    sum_interest = sum(Decimal(i['interest']) for i in schedule)

    companyDetail = Company.objects.get(owner=user)
    companyAddress = CompanyAddress.objects.get(company=companyDetail.id)
    image = ImageCollateral.objects.filter(collateral=pk)
    context = {'collateralDetail': collateralDetail, 'image': image,
               'customerAddress': customerAddress,
               'user': user,
               'sum_interest': sum_interest,
               'companyDetail': companyDetail,
               'customerIdCard': customerIdCard, 'today': today, 'month': month,
               'companyAddress': companyAddress}
    return render(request, 'dashboard/collateral/collateral_detail.html', context)


# ================= create collateral=================

@login_required(login_url='login')
def create_collateral(request):
    customerList = Customer.objects.all()
    loanList = Loan.objects.all()
    if request.method == 'POST':
        # formset = MortgageForm(request.POST, instance=customer)
        # if formset.is_valid():
        title = request.POST['title']
        customer_id = request.POST['cus_name']
        cus_name = Customer.objects.get(id=customer_id)
        loan_id = request.POST['loan']
        loan = Loan.objects.get(id=loan_id)
        description = request.POST['description']
        price = request.POST['price']
        condition = request.POST['condition']
        status = 'active'
        date = request.POST['date']
        image = request.FILES.getlist('image')
        expired_date = request.POST['expired_date']
        collateral_form = Collateral(cus_name=cus_name, loan=loan, title=title,
                                     description=description, condition=condition,
                                     status=status,
                                     price=price, date=date, expired_date=expired_date)
        m = collateral_form
        m.save()
        activity = Activity(
            user=request.user,
            action='create new',
            object=title,
            update_on='',
            table='collateral',
            table_id=m.id
        )
        activity.save()
        messages.success(request, 'Successful creating collateral' + title)
        for i in image:
            ImageCollateral.objects.create(collateral=m, image=i)
        return redirect('collateral_list')
    context = {'customerList': customerList, 'loanList': loanList}
    return render(request, 'dashboard/collateral/collateral_create.html', context)


# ============================= Update Collateral =============================


def update_collateral(request, pk):
    collateral_detail = get_object_or_404(Collateral, id=pk)
    collateralDetail = Collateral.objects.get(id=pk)
    customer = Customer.objects.all()
    loanList = Loan.objects.all()
    customerDetail = Customer.objects.get(id=collateralDetail.cus_name.id)
    loan = Loan.objects.get(id=collateralDetail.loan.id)
    imageCollateral = ImageCollateral.objects.filter(collateral=collateralDetail.id)
    if request.method == 'POST':
        collateral_detail.title = request.POST['title']
        collateral_detail.cus_name = Customer.objects.get(id=collateralDetail.cus_name.id)
        collateral_detail.loan = Loan.objects.get(id=collateralDetail.loan.id)
        collateral_detail.description = request.POST['description']
        collateral_detail.price = request.POST['price']
        collateral_detail.condition = request.POST['condition']
        collateral_detail.status = request.POST['status']
        collateral_detail.date = request.POST['date']
        if 'image' in request.FILES:
            for ic in imageCollateral:
                ic.image = request.FILES['image']
        collateral_detail.save()
        return redirect('collateral_detail', pk)
    context = {'collateralDetail': collateralDetail,
               'loanList': loanList, 'customer': customer,
               'customerDetail': customerDetail,
               'imageCollateral': imageCollateral}

    return render(request, 'dashboard/collateral/collateral_create.html', context)


# ================= create collateral  loan =================

@login_required(login_url='login')
def create_collateral_loan(request, pk):
    loans = Loan.objects.get(id=pk)
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        condition = request.POST['condition']
        price = request.POST['price']
        date = request.POST['date']
        status = 'active'
        image = request.FILES.getlist('image')
        expired_date = request.POST['expired_date']
        collateral_form = Collateral(loan=Loan.objects.get(id=pk), cus_name=Customer.objects.get(id=loans.customer.id),
                                     title=title,
                                     description=description, condition=condition,
                                     status=status,
                                     price=price, date=date, expired_date=expired_date)
        m = collateral_form
        m.save()
        activity = Activity(
            user=request.user,
            action='create new',
            object=title,
            update_on='',
            table='collateral',
            table_id=m.id
        )
        activity.save()
        messages.success(request, 'Successful creating collateral' + title)
        for i in image:
            ImageCollateral.objects.create(collateral=m, image=i)
        return redirect('loan_detail', pk)
    context = {'customer': loans}
    return render(request, 'dashboard/loan/collateral/create_collateral_loan.html', context)


# ============= loan detail ==============
@login_required(login_url='login')
def loan_detail(request, pk):
    loans = Loan.objects.get(id=pk)
    customerId = Customer.objects.get(id=loans.customer_id)
    schedule = loans.create_amortization_schedule()
    total_monthly_amount = sum(Decimal(i['monthly_amount']) for i in schedule)
    total_number_date = sum(Decimal(i['number_date']) for i in schedule)
    total_principle = sum(Decimal(i['principle']) for i in schedule)
    total_interest = sum(Decimal(i['interest']) for i in schedule)
    paybackFilter = Payback.objects.filter(loan=pk)
    total_pay_interest = sum(Decimal(i.interest_paid) for i in paybackFilter)
    total_pay_principle = sum(Decimal(i.principle_paid) for i in paybackFilter)
    total_pay_balance = sum(Decimal(i.balance) for i in paybackFilter)
    total_full_pay_balance = sum(Decimal(i.full_paid) for i in paybackFilter)
    countSchedule = len(schedule) - 1
    # ================= check full pay back to day =============
    today = date.today()
    over_count = []
    have_paid = []
    migrateSchedule = []
    loan_status = loans.loan_status
    count = (paybackFilter.count() / countSchedule) * 100
    acc_amount = 0
    bayback_id = 0
    for over in schedule:
        loan_id = loans.id
        full_off_from = loans.full_off_from
        due_date = over['due_date']
        number = over['number']
        principle = over['principle']
        number_date = over['number_date']
        interest = over['interest']
        monthly_amount = over['monthly_amount']
        acc_amount += Decimal(over['monthly_amount'])
        balance = over['balance']
        over_status = False
        havePaid = False

        if number == 0:
            first_row = True
        else:
            first_row = False
        if due_date < today and number == 0:
            over_status = False
            havePaid = False
            first_row = True
            over_count.append({
                'over_due': over['number'],
            })
        elif due_date < today:
            over_status = True
            havePaid = False
            first_row = False
            over_count.append({
                'over_due': over['number'],
            })

        paybackData = []
        for pay in paybackFilter:
            bayback_id = pay.id
            paybackData.append({
                'balance': balance
            })
            if due_date == pay.due_date and Decimal(monthly_amount) == Decimal(pay.balance):
                havePaid = True
                over_status = False
                have_paid.append({
                    'over_due': pay.id,
                    'balance': pay.balance,
                })
        count_overdue = sum('over_due' in i for i in over_count) - sum('over_due' in i for i in have_paid)
        if paybackFilter.count() > loans.full_off_from:
            full_pay_button = True
        else:
            full_pay_button = False
        check_full_paid = sum(i.full_paid for i in paybackFilter)
        if check_full_paid > 0:
            s = Loan(id=pk, loan_amount=loans.loan_amount, customer=loans.customer,
                     loan_number_id=loans.loan_number_id, loan_cycle_type=loans.loan_cycle_type,
                     number_of_cycle=loans.number_of_cycle, interest_rate_per_cycle=loans.interest_rate_per_cycle,
                     loan_date=loans.loan_date, is_set_first_payment_date=loans.is_set_first_payment_date,
                     first_payment_date=loans.first_payment_date, rate_calculate_method=loans.rate_calculate_method,
                     payment_schedule=loans.payment_schedule,
                     full_off_from=full_off_from,
                     loan_status='completed')
            s.save()
        else:
            if count == 100:
                s = Loan(id=pk, loan_amount=loans.loan_amount, customer=loans.customer,
                         loan_number_id=loans.loan_number_id, loan_cycle_type=loans.loan_cycle_type,
                         number_of_cycle=loans.number_of_cycle, interest_rate_per_cycle=loans.interest_rate_per_cycle,
                         loan_date=loans.loan_date, is_set_first_payment_date=loans.is_set_first_payment_date,
                         first_payment_date=loans.first_payment_date, rate_calculate_method=loans.rate_calculate_method,
                         payment_schedule=loans.payment_schedule,
                         full_off_from=full_off_from,
                         loan_status='completed')
                s.save()
            elif count_overdue > 10:
                s = Loan(id=pk, loan_amount=loans.loan_amount, customer=loans.customer,
                         loan_number_id=loans.loan_number_id, loan_cycle_type=loans.loan_cycle_type,
                         number_of_cycle=loans.number_of_cycle, interest_rate_per_cycle=loans.interest_rate_per_cycle,
                         loan_date=loans.loan_date, is_set_first_payment_date=loans.is_set_first_payment_date,
                         first_payment_date=loans.first_payment_date, rate_calculate_method=loans.rate_calculate_method,
                         payment_schedule=loans.payment_schedule,
                         full_off_from=full_off_from,
                         loan_status='lost')
                s.save()
            else:
                s = Loan(id=pk, loan_amount=loans.loan_amount, customer=loans.customer,
                         loan_number_id=loans.loan_number_id, loan_cycle_type=loans.loan_cycle_type,
                         number_of_cycle=loans.number_of_cycle, interest_rate_per_cycle=loans.interest_rate_per_cycle,
                         loan_date=loans.loan_date, is_set_first_payment_date=loans.is_set_first_payment_date,
                         first_payment_date=loans.first_payment_date, rate_calculate_method=loans.rate_calculate_method,
                         payment_schedule=loans.payment_schedule,
                         full_off_from=full_off_from,
                         loan_status='on going')
                s.save()

        migrateSchedule.append({
            'id': loan_id,
            'payback_id': bayback_id,
            'countSchedule': countSchedule,
            'progress': count,
            'due_date': due_date,
            'over_count': over_count,
            'customer': loans.customer.profile_img,
            'name': loans.customer.name,
            'number': number,
            'name_kh': loans.customer.name_kh,
            'loan_amount': loans.loan_amount,
            'interest_rate_per_cycle': loans.interest_rate_per_cycle,
            'number_date': number_date,
            'principle': principle,
            'interest': interest,
            'monthly_amount': monthly_amount,
            'balance': balance,
            'status': loans.loan_status,
            'loan_cycle_type': loans.loan_cycle_type,
            'number_of_cycle': loans.number_of_cycle,
            'over_status': over_status,
            'havePaid': havePaid,
            'first_row': first_row,
            'loan_status': loan_status,
            'full_pay_button': full_pay_button,
            'returned': acc_amount,
        })
    try:
        collateralID = Collateral.objects.filter(loan=loans.id)
        collateralList = []
        for item in collateralID:
            id = item.id
            title = item.title
            description = item.description
            price = item.price
            dates = item.date
            expired_date = item.expired_date
            image = ''
            images = ImageCollateral.objects.filter(collateral=id)
            for i in images:
                image = i.image
            collateralList.append({
                'id': id,
                'title': title,
                'description': description,
                'price': price,
                'dates': dates,
                'expired_date': expired_date,
                'image': image,
            })
    except Collateral.DoesNotExist:
        collateralID = False
    try:
        customerAddress = CustomerAddress.objects.get(customer_id=customerId.id)
    except CustomerAddress.DoesNotExist:
        customerAddress = None
    context = {'loanList': loans, 'schedule': schedule,
               'customerId': customerId,
               'paybackFilter': paybackFilter,
               'total_monthly_amount': total_monthly_amount,
               'total_interest': total_interest,
               'total_principle': total_principle,
               'total_number_date': total_number_date,
               'collateralID': collateralList,
               'migrateSchedule': migrateSchedule,
               'today': today,
               'total_pay_interest': total_pay_interest,
               'total_pay_principle': total_pay_principle,
               'total_pay_balance': total_pay_balance,
               'pawList': pawList,
               'customerAddress': customerAddress}
    return render(request, 'dashboard/loan/loan_detail.html', context)


# ================== loan list =====================


@login_required(login_url='login')
def loan(request):
    loanList = Loan.objects.all().order_by('-id')

    countPayback = []
    for loan in loanList:
        schedule = loan.create_amortization_schedule()
        paybackFilter = Payback.objects.filter(loan=loan.id)
        countSchedule = len(schedule) - 1

        today = date.today()
        over_count = []
        have_paid = []
        detail_loan = []
        del schedule[0]
        for over in schedule:
            due_date = over['due_date']
            monthly_amount = over['monthly_amount']
            detail_loan.append({
                'monthly_amount': Decimal(monthly_amount),
            })
            if due_date < today:
                over_count.append({
                    'over_due': 0,
                    'balance': Decimal(monthly_amount),
                })
            for pay in paybackFilter:
                if due_date == pay.due_date:
                    have_paid.append({
                        'over_due': pay.id,
                        'balance': pay.balance,
                        'full_paid': pay.full_paid
                    })
        count_overdue = sum('over_due' in i for i in over_count) - sum('over_due' in i for i in have_paid)
        total_over_due = sum(i['balance'] for i in over_count) - sum(i['balance'] for i in have_paid)
        total_full_paid = sum(i['full_paid'] for i in have_paid)
        total_payback = sum(i['balance'] for i in have_paid) + total_full_paid
        if loan.loan_status == 'completed':
            count = 100
            total_remaining = 0.000
        else:
            count = (paybackFilter.count() / countSchedule) * 100
            total_remaining = sum(i['monthly_amount'] for i in detail_loan) - total_payback

        if count_overdue < 0:
            count_overdue = 0
        else:
            count_overdue = sum('over_due' in i for i in over_count) - sum('over_due' in i for i in have_paid)
        countPayback.append({
            'id': loan.id,
            'countSchedule': countSchedule,
            'progress': count,
            'customer': loan.customer.profile_img,
            'name': loan.customer.name,
            'name_kh': loan.customer.name_kh,
            'loan_amount': loan.loan_amount,
            'interest_rate_per_cycle': loan.interest_rate_per_cycle,
            'due_date': loan.loan_date,
            'status': loan.loan_status,
            'total_over_due': total_over_due,
            'total_payback': total_payback,
            'loan_cycle_type': loan.loan_cycle_type,
            'number_of_cycle': loan.number_of_cycle,
            'count_Overdue_date': count_overdue,
            'total_remaining': total_remaining
        })
    loan_filter = LoanFilter(request.GET, queryset=loanList)
    loanData = loan_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(loanData, 5)
    try:
        loanData = paginator.page(page)
    except PageNotAnInteger:
        loanData = paginator.page(1)
    except EmptyPage:
        loanData = paginator.page(paginator.num_pages)
    context = {'loanList': loanList,
               'loanSearchForm': loanSearchForm,
               'loanData': loanData,
               'paginator': paginator,
               'countPayback': countPayback}
    return render(request, 'dashboard/loan/loan_list.html', context)


# ===================== Loan List Search ====================
@login_required(login_url='login')
def search_loan(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        loanList = request.POST.get('loanList')
        query_loan = Loan.objects.filter(Q(customer__name__icontains=loanList) |
                                         Q(customer__name_kh__icontains=loanList) |
                                         Q(loan_amount__icontains=loanList) |
                                         Q(loan_number_id__icontains=loanList) |
                                         Q(loan_status__icontains=loanList)
                                         )

        if len(query_loan) > 0 and len(loanList) > 0:
            data = []
            for i in query_loan:
                item = {
                    'id': i.id,
                    'name': i.customer.name,
                    'name_kh': i.customer.name_kh,
                    'profile_image': i.customer.profile_img.url if i.customer.profile_img else '',
                    'loan_status': i.loan_status,
                    'loan_amount': i.loan_amount,
                }
                data.append(item)
            res = data
        else:
            res = 'No loan found with what name'
        return JsonResponse({'data': res})


# ================= create  loan =========================

@login_required(login_url='login')
def loanCreate(request):
    customer_list = Customer.objects.all()
    form = LoanDataForm()

    context = {'customerList': customer_list, 'form': form}
    if request.method == 'POST':
        customer_id = request.POST['customer']
        customer = Customer.objects.get(id=customer_id)
        collateral = Collateral.objects.get(id=customer.collateral)
        form = LoanDataForm(request.POST)
        if form.is_valid():
            form.instance.customer = customer
            form.instance.collateral = collateral
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object='on' + customer.name,
                update_on='',
                table='loan',
                table_id=m.id
            )
            activity.save()
            messages.success(request, 'Loan has been created!')
        return redirect('loan')
    else:

        return render(request, 'dashboard/loan/loan_create.html', context)


# =========== update loan ========

@login_required(login_url='login')
def loan_update(request, pk):
    loan_id = Loan.objects.get(id=pk)
    form = LoanDataForm(instance=loan_id)
    customerDetail = Customer.objects.get(id=loan_id.customer.id)

    if request.method == 'POST':
        form = LoanDataForm(request.POST or None, instance=loan_id)
        if form.is_valid():
            m = form.save()
            activity = Activity(
                user=request.user,
                action='update new',
                object='on' + customerDetail.name,
                update_on='',
                table='loan',
                table_id=m.id
            )
            activity.save()
            return redirect('loan_detail', loan_id.id)
    context = {'form': form, 'loan_id': loan_id, 'customerDetail': customerDetail}
    return render(request, 'dashboard/customer/loan/create_customer_loan_form.html', context)


def human_format(num):
    magnitube = 0
    while abs(num) >= 1000:
        magnitube += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitube])


# ============ Dashboard ================


@login_required(login_url='login')
def dashboard(request):
    today = datetime.today()
    month = today.month - 1
    year = today.year

    # === Invest return payback ==============================

    last_month_payback = Payback.objects.filter(due_date__month=month, due_date__year=year).values('balance')
    this_month_payback = Payback.objects.filter(due_date__month=today.month, due_date__year=today.year).values(
        'balance')
    total_last_month_payback = sum(i['balance'] for i in last_month_payback)
    total_this_month_payback = sum(i['balance'] for i in this_month_payback)

    if total_this_month_payback == 0 and total_last_month_payback == 0:
        total_invest_return = 0
    elif total_last_month_payback == 0 or total_this_month_payback == 0:
        total_invest_return = 0
    else:
        total_invest_return = ((total_this_month_payback - total_last_month_payback) / decimal.Decimal(
            total_last_month_payback)) * 100

    # =========== total invest return percentage =================

    if total_invest_return > 0:
        result_invest_return = total_invest_return
    else:
        result_invest_return = total_invest_return * -1
    int_this_month_payback = human_format(int(total_this_month_payback))
    int_last_month_payback = human_format(int(total_last_month_payback))

    # ====== Earning =========

    last_month_earn = Payback.objects.filter(due_date__month=month, due_date__year=year).values('interest_paid')
    this_month_earn = Payback.objects.filter(due_date__month=today.month, due_date__year=today.year).values(
        'interest_paid')
    earning_last = sum(i['interest_paid'] for i in last_month_earn)
    earning_this = sum(i['interest_paid'] for i in this_month_earn)

    if earning_this == 0 and earning_last == 0:
        total_earn = 0
    elif earning_last == 0 or earning_this == 0:
        total_earn = 0
    else:
        total_earn = ((earning_this - earning_last) / decimal.Decimal(earning_last)) * 100

    # =========== total earning percentage =================
    if total_earn > 0:
        result_total_earn = total_earn
    else:
        result_total_earn = total_earn * -1
    int_this_earn = human_format(int(earning_this))
    int_last_earn = human_format(int(earning_last))

    # ====== Loan Amount  =========
    last_month_loan = Loan.objects.filter(loan_date__month=month, loan_date__year=year).values('loan_amount')
    this_month_loan = Loan.objects.filter(loan_date__month=today.month, loan_date__year=today.year).values(
        'loan_amount')
    total_this_month = sum(i['loan_amount'] for i in this_month_loan)
    total_last_month = sum(i['loan_amount'] for i in last_month_loan)

    if total_this_month == 0 and total_last_month == 0:
        total_invest = 0
    elif total_last_month == 0 or total_this_month == 0:
        total_invest = 0
    else:
        total_invest = ((total_this_month - total_last_month) / decimal.Decimal(total_last_month)) * 100
    # try:
    #     total_invest = ((total_this_month - total_last_month) / decimal.Decimal(total_last_month)) * 100
    # except decimal.DivisionByZero:
    #     total_invest = 0

    # =========== total invest percentage =================

    if total_invest > 0:
        result_invest = total_invest
    else:
        result_invest = total_invest * -1

    int_last_month = human_format(int(total_last_month))
    int_this_month = human_format(int(total_this_month))
    # Calculate the percentage difference
    # bong = 100 - (total_this_month * 100 / total_last_month )

    # =========== sum data in dashboard =====================
    payback_data = Payback.objects.all()
    total = PawPay.objects.all()
    loan_amount = Loan.objects.aggregate(Sum('loan_amount'))
    tol_principle = sum(i.principle_paid for i in payback_data) + sum(i.full_paid for i in payback_data)
    tol_payback = sum(i.balance for i in payback_data) + sum(i.full_paid for i in payback_data)
    tol_payPaw = sum(i.pay_rate for i in total)
    tol_interest = sum(i.interest_paid for i in payback_data) + tol_payPaw

    # ================= count data number dashboard ===================
    count_loan = Loan.objects.all().count()
    count_loan_this_month = Loan.objects.filter(timestamp__month=today.month, timestamp__year=today.year).count()
    customer = Customer.objects.all()
    customers = customer.count()
    count_customers_this_month = Customer.objects.filter(date_created__month=today.month,
                                                         date_created__year=today.year).count()
    # Count Paw transactions
    count_paw_total = Paw.objects.all().count()
    count_paw_this_month = Paw.objects.filter(timestamp__month=today.month, timestamp__year=today.year).count()

    # ============================== Chart Dashboard ============================
    total_current_month_interest = []
    total_current_month_principle = []
    total_current_month_paid = []
    month_name = []
    choose_month = 'This Year'
    if request.method == 'POST':
        if 'monthly' in request.POST:
            choose_month = request.POST['monthly']
        else:
            choose_month = 'This Year'
    if choose_month == 'Month':
        today = datetime.today()
        month = today.month
        year = today.year
        start_date = datetime(year=year, month=month, day=1)
        end_date = start_date.replace(day=28) + timedelta(days=4)
        last_day = (end_date - timedelta(days=end_date.day)).day
        for day in range(1, last_day + 1):
            date = datetime(year=year, month=month, day=day)
            current_month_interest = Payback.objects.filter(due_date=date).values('interest_paid')
            current_month_principle = Payback.objects.filter(due_date=date).values('principle_paid')
            current_month_paid = Payback.objects.filter(due_date=date).values('balance')
            total_current_day_interest = sum(i['interest_paid'] for i in current_month_interest)
            total_current_day_principle = sum(i['principle_paid'] for i in current_month_principle)
            total_current_day_paid = sum(i['balance'] for i in current_month_paid)
            total_current_month_interest.append({
                'total_current_day_interest': total_current_day_interest,
            })
            total_current_month_principle.append({
                'total_current_day_principle': total_current_day_principle,
            })
            total_current_month_paid.append({
                'total_current_day_paid': total_current_day_paid,
            })
            month_name.append({
                'name': day
            })
    elif choose_month == 'Last Month':
        today = datetime.today()
        month = today.month - 1
        year = today.year
        start_date = datetime(year=year, month=month, day=1)
        end_date = start_date.replace(day=28) + timedelta(days=4)
        last_day = (end_date - timedelta(days=end_date.day)).day
        for day in range(1, last_day + 1):
            date = datetime(year=year, month=month, day=day)
            current_month_interest = Payback.objects.filter(due_date=date).values('interest_paid')
            current_month_principle = Payback.objects.filter(due_date=date).values('principle_paid')
            current_month_paid = Payback.objects.filter(due_date=date).values('balance')
            total_current_day_interest = sum(i['interest_paid'] for i in current_month_interest)
            total_current_day_principle = sum(i['principle_paid'] for i in current_month_principle)
            total_current_day_paid = sum(i['balance'] for i in current_month_paid)
            total_current_month_interest.append({
                'total_current_day_interest': total_current_day_interest,
            })
            total_current_month_principle.append({
                'total_current_day_principle': total_current_day_principle,
            })
            total_current_month_paid.append({
                'total_current_day_paid': total_current_day_paid,
            })
            month_name.append({
                'name': day
            })
    elif choose_month == 'This Year':
        current_year = today.year
        for month in range(1, 13):
            name = calendar.month_name[month]
            current_month_interest = Payback.objects.filter(due_date__year=current_year, due_date__month=month).values(
                'interest_paid')
            current_month_principle = Payback.objects.filter(due_date__year=current_year, due_date__month=month).values(
                'principle_paid')
            current_month_paid = Payback.objects.filter(due_date__year=current_year, due_date__month=month).values(
                'balance')
            total_current_year_interest = sum(i['interest_paid'] for i in current_month_interest)
            total_current_year_principle = sum(i['principle_paid'] for i in current_month_principle)
            total_current_year_paid = sum(i['balance'] for i in current_month_paid)
            total_current_month_interest.append({
                'total_current_year_interest': total_current_year_interest,
            })
            total_current_month_principle.append({
                'total_current_year_principle': total_current_year_principle,
            })
            total_current_month_paid.append({
                'total_current_year_paid': total_current_year_paid,
            })
            month_name.append({
                'name': name
            })
    elif choose_month == 'Last Year':
        current_year = today.year - 1
        for month in range(1, 13):
            name = calendar.month_name[month]
            current_month_interest = Payback.objects.filter(due_date__year=current_year,
                                                            due_date__month=month).values('interest_paid')
            current_month_principle = Payback.objects.filter(due_date__year=current_year,
                                                             due_date__month=month).values('principle_paid')
            current_month_paid = Payback.objects.filter(due_date__year=current_year, due_date__month=month).values(
                'balance')
            total_current_year_interest = sum(i['interest_paid'] for i in current_month_interest)
            total_current_year_principle = sum(i['principle_paid'] for i in current_month_principle)
            total_current_year_paid = sum(i['balance'] for i in current_month_paid)
            total_current_month_interest.append({
                'total_current_month_interest': total_current_year_interest,
            })
            total_current_month_principle.append({
                'total_current_year_principle': total_current_year_principle,
            })
            total_current_month_paid.append({
                'total_current_year_paid': total_current_year_paid,
            })
            month_name.append({
                'name': name
            })

            # ========= Default ===========
    else:
        current_year = today.year
        for month in range(1, 13):
            name = calendar.month_name[month]
            current_month_interest = Payback.objects.filter(due_date__year=current_year,
                                                            due_date__month=month).values('interest_paid')
            current_month_principle = Payback.objects.filter(due_date__year=current_year,
                                                             due_date__month=month).values('principle_paid')
            current_month_paid = Payback.objects.filter(due_date__year=current_year, due_date__month=month).values(
                'balance')
            total_current_year_interest = sum(i['interest_paid'] for i in current_month_interest)
            total_current_year_principle = sum(i['principle_paid'] for i in current_month_principle)
            total_current_year_paid = sum(i['balance'] for i in current_month_paid)
            total_current_month_interest.append({
                'total_current_month_interest': total_current_year_interest,
            })
            total_current_month_principle.append({
                'total_current_year_principle': total_current_year_principle,
            })
            total_current_month_paid.append({
                'total_current_year_paid': total_current_year_paid,
            })
            month_name.append({
                'name': name
            })
    # =============== filter number top of data ==================
    payback = Payback.objects.all().order_by('-id')[:10]
    activities = Activity.objects.all().order_by('-timestamp')[:10]

    loans = Loan.objects.all()
    over_due_date_schedule = []
    today = today.date()
    countPaw = Paw.objects.all().count()
    for loan in loans:
        overschedule = loan.create_amortization_schedule()
        del overschedule[0]
        for over in overschedule:
            due_date = over['due_date']
            balance = over['monthly_amount']
            id = loan.id
            customerImage = loan.customer.profile_img
            customer = loan.customer
            paybackFilter = Payback.objects.filter(loan=loan)
            if due_date < today:
                display = []
                for j in paybackFilter:
                    if over["due_date"] == j.due_date:
                        display.append({
                            "due_date": j.due_date,
                        })
                        over["payment_due_date"] = j.due_date
                over_due_date_schedule.append({
                    'due_date': due_date,
                    'balance': balance,
                    'loan': id,
                    'loan_number_id': loan.loan_number_id,
                    'display': display,
                    'until': (today - due_date).days,
                    'customerImage': customerImage,
                    'customer': customer,
                })
    current_lang = get_language()
    
    context = {
        'countPaw': countPaw,
        'loan_amount': loan_amount,
        'tol_interest': tol_interest,
        'tol_payback': tol_payback,
        'tol_principle': tol_principle,
        'activities': activities,
        'customer': customers,
        'count_loan': count_loan,
        'int_last_month': int_last_month,
        'int_this_month': int_this_month,
        'total_last_month_payback': total_last_month_payback,
        'total_this_month_payback': total_this_month_payback,
        'int_this_month_payback': int_this_month_payback,
        'int_last_month_payback': int_last_month_payback,
        'total_last_month': total_last_month,
        'total_this_month': total_this_month,
        'earning_this': earning_this,
        'earning_last': earning_last,
        'paybackList': payback,
        'total_invest': total_invest,
        'result_invest': result_invest,
        'total_invest_return': total_invest_return,
        'result_invest_return': result_invest_return,
        'total_earn': total_earn,
        'int_this_earn': int_this_earn,
        'int_last_earn': int_last_earn,
        'result_total_earn': result_total_earn,
        'count_loan_this_month': count_loan_this_month,
        'count_customers_this_month': count_customers_this_month,
        'total_current_month_interest': total_current_month_interest,
        'total_current_month_principle': total_current_month_principle,
        'total_current_month_paid': total_current_month_paid,
        'choose_month': choose_month,
        'month_name': month_name,
        'over_due_date_schedule': over_due_date_schedule,
        'count_paw_total': count_paw_total,
        'count_paw_this_month': count_paw_this_month,
        'current_lang': current_lang
    }

    

    return render(request, 'dashboard/index.html', context)
    

# ========== recent activity  list===============
@login_required(login_url='login')
def recent_activities(request):
    activitiesList = Activity.objects.all().order_by('-timestamp')
    activities_filter = ActivityFilter(request.GET, queryset=activitiesList)
    activities = activities_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(activities, 9)
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    context = {'activities': activities, 'paginator': paginator}
    return render(request, 'dashboard/recent_activities/recent_activities.html', context)


# ======================== delete activities ============================


def delete_all_activities(request):
    activities_deleted_all = Activity.objects.all()
    activities_deleted_all.delete()
    return redirect('recent_activities')


def delete_activities(request, pk):
    activities_item = Activity.objects.get(id=pk).delete()
    context = {'activities_item': activities_item}
    return redirect('recent_activities')


# ====================== create loan for customer =====================


@login_required(login_url='login')
@admin_only
def create_loan_for_customer(request, pk):
    customerId = Customer.objects.get(id=pk)
    today = date.today()
    form = LoanDataForm()
    if request.method == 'POST':
        form = LoanDataForm(request.POST)
        if form.is_valid():
            form.instance.customer = customerId
            m = form.save()
            activity = Activity(
                user=request.user,
                action='create new',
                object='on' + customerId.name,
                update_on='',
                table='loan',
                table_id=m.id
            )
            activity.save()
            messages.success(request, 'Create successfully !')
        return redirect('customer-detail', pk)
    else:
        messages.error(request, 'Cancel create loan.')
        context = {'customerId': customerId, 'form': form, 'today': today}
        return render(request, 'dashboard/customer/loan/create_customer_loan_form.html', context)


# ==================== loan detail from customer ======================

@login_required(login_url='login')
def loan_detail_from_customer(request, pk):
    loans = Loan.objects.get(id=pk)
    try:
        collateralID = Collateral.objects.filter(loan=loans.id)
    except Collateral.DoesNotExist:
        collateralID = False
    customerId = Customer.objects.get(id=loans.customer_id)
    schedule = loans.create_amortization_schedule()
    paybackFilter = Payback.objects.filter(loan=pk)
    today = date.today()
    for i in range(len(schedule)):
        found = False
        for j in range(len(paybackFilter)):
            if schedule[i]["due_date"] == paybackFilter[j].due_date and float(schedule[i]["monthly_amount"]) == float(
                    paybackFilter[j].balance):
                schedule[i]["payment_due_date"] = paybackFilter[j].due_date
                found = True

        if not found:
            schedule[i]["payment_due_date"] = "None"
    try:
        customerAddress = CustomerAddress.objects.get(customer_id=customerId.id)

    except CustomerAddress.DoesNotExist:
        customerAddress = None
    context = {'loanList': loans, 'schedule': schedule,
               'customerId': customerId,
               'paybackFilter': paybackFilter,
               'collateralID': collateralID,
               'today': today,
               'customerAddress': customerAddress}
    return render(request, 'dashboard/customer/loan/loan_detail.html', context)


# ================= payback ================

def payback(request):
    paybackList = Payback.objects.all().order_by('-id')
    payback_filter = PaybackFilter(request.GET, queryset=paybackList)
    payBack = payback_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(payBack, 9)
    try:
        payBack = paginator.page(page)

    except PageNotAnInteger:
        payBack = paginator.page(1)
    except EmptyPage:
        payBack = paginator.page(paginator.num_pages)

    context = {'paybackList': paybackList, 'payBack': payBack, 'paginator': paginator}
    return render(request, 'dashboard/payment/payback_list.html', context)


# ================= filter payback loan id =====================
def filter_payback_by_loan_id(request, pk):
    paybacks = Payback.objects.filter(loan=pk)
    total_interest_paid = paybacks.aggregate(Sum('interest_paid'))['interest_paid__sum']
    total_principle_paid = paybacks.aggregate(Sum('principle_paid'))['principle_paid__sum']
    total_balance = paybacks.aggregate(Sum('balance'))['balance__sum']
    loansDetail = Loan.objects.get(id=pk)
    schedule = loansDetail.create_amortization_schedule()
    countSchedule = len(schedule)
    countPayback = (paybacks.count() / countSchedule) * 100
    context = {'loansDetail': loansDetail, 'countPayback': countPayback,
               'total_interest_paid': total_interest_paid,
               'total_principle_paid': total_principle_paid,
               'total_balance': total_balance,
               'countschedule': countSchedule}
    return render(request, 'dashboard/payment/filter_loan_payback.html', context)


# ==================== create payback ===============
@login_required(login_url='login')
def create_payback(request, pk):
    loan = Loan.objects.get(id=pk)
    # paybackFilter = Payback.objects.get(loan=loan.id)
    if request.method == 'POST':
        interest_paid = request.POST['interest_paid']
        principle_paid = request.POST['principle_paid']
        balance = request.POST['balance']
        due_date = request.POST['due_date']
        pay_date = request.POST['pay_date']
        attached_file = request.FILES.get('attached_file')
        full_paid = request.POST.get('full_paid', False)
        data = Payback(loan=Loan.objects.get(id=pk),
                       customer=Customer.objects.get(id=loan.customer.id),
                       interest_paid=interest_paid, principle_paid=principle_paid,
                       attached_file=attached_file,
                       balance=balance, full_paid=full_paid,
                       due_date=due_date, pay_date=pay_date)
        m = data
        m.save()
        activity = Activity(
            user=request.user,
            action='create new',
            object='on loan' + loan.loan_number_id,
            update_on='',
            table='payback',
            table_id=m.id
        )
        activity.save()
        messages.success(request, 'Payment has been processed successful')
        return redirect('loan_detail', pk)
    else:
        messages.error(request, 'Failed payback')
    context = {}
    return render(request, 'dashboard/payment/payback_list.html', context)


# ==================== create payback ===============
@login_required(login_url='login')
def create_full_payback(request, pk):
    loan = Loan.objects.get(id=pk)
    # paybackFilter = Payback.objects.get(loan=loan.id)
    if request.method == 'POST':
        interest_paid = request.POST['interest_paid']
        principle_paid = request.POST['principle_paid']
        balance = request.POST['balance']
        due_date = request.POST['due_date']
        pay_date = request.POST['pay_date']
        attached_file = request.FILES.get('attached_file')
        full_paid = request.POST['full_paid']
        data = Payback(loan=Loan.objects.get(id=pk),
                       customer=Customer.objects.get(id=loan.customer.id),
                       interest_paid=interest_paid, principle_paid=principle_paid,
                       attached_file=attached_file,
                       balance=balance, full_paid=full_paid,
                       due_date=due_date, pay_date=pay_date)
        m = data
        m.save()
        Loan(id=loan.id, customer=loan.customer, loan_number_id=loan.loan_number_id,
             loan_amount=loan.loan_amount, loan_cycle_type=loan.loan_cycle_type,
             number_of_cycle=loan.number_of_cycle,
             interest_rate_per_cycle=loan.interest_rate_per_cycle, loan_date=loan.loan_date,
             loan_status='completed', full_off_from=loan.full_off_from,
             is_set_first_payment_date=loan.is_set_first_payment_date,
             first_payment_date=loan.first_payment_date,
             rate_calculate_method=loan.rate_calculate_method,
             payment_schedule=loan.payment_schedule)
        activity = Activity(
            user=request.user,
            action='create new',
            object='on loan' + loan.loan_number_id,
            update_on='',
            table='payback',
            table_id=m.id
        )
        activity.save()
        messages.success(request, 'Payment has been processed successful')
        return redirect('loan_detail', pk)
    else:
        messages.error(request, 'Failed payback')
    context = {}
    return render(request, 'dashboard/payment/payback_list.html', context)


# ============ payback detail =================

def payback_detail(request, pk):
    payBackId = Payback.objects.get(id=pk)
    context = {"paybackDetail": payBackId}
    if request.method == 'POST':
        payBackId.delete()
    return render(request, 'dashboard/payment/payback_detail.html', context)


#  ======================================== delete payback =====================================
@login_required(login_url='login')
def delete_collateral(request, pk):
    payCollateral = Collateral.objects.get(id=pk)
    if request.method == "POST":
        payCollateral.delete()
        activity = Activity(
            user=request.user,
            action='delete',
            object=payCollateral.title,
            update_on=payCollateral.title,
            table='collateral',
            table_id=0
        )
        activity.save()
        return redirect('collateral_list')
    context = {'item': payCollateral}
    return render(request, 'dashboard/collateral/collateral_detail.html', context)


# ===================== collateral list ====================

def collateral_list(request):
    collateral_list = Collateral.objects.all().order_by('-id')
    collateralList = []
    today = datetime.today().date()
    for collateral in collateral_list:
        id = collateral.id
        title = collateral.title
        description = collateral.description
        price = collateral.price
        date = collateral.date
        status = collateral.status
        expired_date = collateral.expired_date
        customer = collateral.cus_name
        dayExpired = expired_date - today

        item = ''
        imageCollateral = ImageCollateral.objects.filter(collateral=id)
        for item in imageCollateral:
            item = item.image
        collateralList.append({
            'id': id,
            'customer': customer,
            'title': title,
            'description': description,
            'price': price,
            'date': date,
            'expired_date': expired_date,
            'image': item,
            'status': status,
            'dayExpired': dayExpired.days
        })

    context = {'collateralList': collateralList}
    return render(request, 'dashboard/collateral/collateral_list.html', context)


def collateral_create(request):
    return render(request, 'dashboard/collateral/collateral_create.html')


# ======================= ID CARD  ===========================

def create_id_card(request, pk):
    customerDetail = Customer.objects.get(id=pk)
    form = imageIdCardForm()
    if request.method == 'POST':
        card_type = request.POST['card_type']
        card_number = request.POST['card_number']
        card_dateline = request.POST['card_deadline']
        image_url = request.FILES.getlist('image_url')
        form = IdCard(customer=Customer.objects.get(id=pk),
                      card_type=card_type, card_number=card_number,
                      card_deadline=card_dateline)
        id_card = form
        form.save()
        for i in image_url:
            imageIdCard.objects.create(id_card=id_card, image_url=i)
        activity = Activity(
            user=request.user,
            action='create new',
            object='on',
            update_on='',
            table='ID CARD',
            table_id=id_card.id
        )
        activity.save()
        return redirect('customer-detail', pk)
    context = {'customerDetail': customerDetail, 'form': form}
    return render(request, 'dashboard/customer/id_card/id_card_form.html', context)


# ======================= ID CARD Detail ===========================

def id_card_detail(request, pk):
    idCardDetail = IdCard.objects.get(id=pk)
    customerDetail = Customer.objects.get(id=idCardDetail.customer.id)
    id_cardImage = imageIdCard.objects.filter(id_card=idCardDetail.id)
    context = {'idcardDetail': idCardDetail, 'customerDetail': customerDetail, 'id_cardImage': id_cardImage}
    return render(request, 'dashboard/customer/id_card/id_card_detail.html', context)


# =========================== Delete Id Card ==============

def delete_id_card(request, pk):
    idCardDetail = IdCard.objects.get(id=pk)
    customer_detail = Customer.objects.get(id=idCardDetail.customer.id)
    if request.method == 'POST':
        idCardDetail.delete()
        return redirect('customer-detail', customer_detail.id)

    # ====================== update id card ================


def update_id_card(request, pk):
    customerDetail = Customer.objects.get(id=pk)
    idcardDetail = IdCard.objects.get(customer=customerDetail.id)
    imageList = imageIdCard.objects.filter(id_card=idcardDetail.id)
    if request.method == 'POST':
        idcardDetail.card_type = request.POST['card_type']
        idcardDetail.card_number = request.POST['card_number']
        idcardDetail.card_dateline = request.POST['card_deadline']
        idcardDetail.card_dateline = request.POST['card_deadline']
        idcardDetail.customer = customerDetail
        idcardDetail.save()

        return redirect('id_card_detail', idcardDetail.id)

    if request.method == 'POST':
        for image in imageList:
            image.image_url = request.FILES['image_url']
            image.save()
    context = {'idcardDetail': idcardDetail, 'customerDetail': customerDetail,
               'imageList': imageList}
    return render(request, 'dashboard/customer/id_card/id_card_form.html', context)


def detail_id_card(request):
    return render(request, 'dashboard/customer/id_card/id_card_detail.html')


# ============ Report =================
def Overdue_date(request):
    loans = Loan.objects.all()
    today = date.today()
    try:
        loans = Loan.objects.all()
        over_due_date_schedule = []
    except Loan.DoesNotExist:
        over_due_date_schedule = []
    for loan in loans:
        overschedule = loan.create_amortization_schedule()
        sorted_loans = sorted(overschedule, key=lambda x: x['due_date'] < today)
        if any(x['due_date'] < today for x in overschedule):
            sorted_loans = sorted(sorted_loans, key=lambda x: x['due_date'] >= today)
        for i in sorted_loans:
            due_date = i['due_date']
            balance = i['balance']
            id = loan.id
            customerImage = loan.customer.profile_img
            paybackFilter = Payback.objects.filter(loan=loan)
            if due_date < today:
                display = []
                for j in paybackFilter:
                    if i["due_date"] == j.due_date:
                        display.append({
                            "due_date": j.due_date
                        })
                        i["payment_due_date"] = j.due_date
                over_due_date_schedule.append({
                    'due_date': due_date,
                    'balance': balance,
                    'loan': id,
                    'display': display,
                    'customerImage': customerImage
                })
    context = {
        'over_due_date_schedule': over_due_date_schedule,
        'loan': loans
    }
    return render(request, 'dashboard/report/Report_Over_dute.html', context)


def full_paid_pack(request, pk):
    loan = Loan.objects.get(id=pk)
    schedule_loan = loan.create_amortization_schedule()
    paybackFilter = Payback.objects.filter(loan=pk)
    total_pay = sum(Decimal(i.principle_paid) for i in paybackFilter)
    total_schedule = sum(Decimal(i['principle']) for i in schedule_loan)
    last_pay = total_schedule - total_pay
    # for pay in paybackFilter:

    context = {'loan': loan}
    return render(request, 'dashboard/loan/full_paid.html', context)


# =============== Setting user ======================
# Device information 

def setting(request, pk):
    user = request.user
    user_info = User.objects.get(id=pk)
    # profile = OwnerLogo.objects.get(user=user)
    profile = OwnerLogo.objects.filter(user=user).order_by('-timestamp').first()
    # Check if a logo was found, otherwise use a default logo
    if not profile:
        profile = None
    OS = platform.system()  # Device information
    # Execute the ipconfig command and redirect the output to a file
    os.system('ipconfig /all > output.txt')

    # Read the contents of the file into a variable
    with open('output.txt', 'r') as f:
        output = f.read()

    # Remove the temporary file
    os.remove('output.txt')

    # Find the sections for the wireless and Ethernet adapters
    wireless_section = re.search(r'Wireless LAN adapter Wi-Fi.*?(IPv4 Address.*?)\n\n', output, re.DOTALL)
    ethernet_section = re.search(r'Ethernet adapter Ethernet.*?(IPv4 Address.*?)\n\n', output, re.DOTALL)
    if wireless_section:
        # Extract the IPv4 addresses from each section
        wireless_ipv4 = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', wireless_section.group(1)).group(0)
    else:
        wireless_ipv4 = None

    if ethernet_section:
        ethernet_ipv4 = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ethernet_section.group(1)).group(0)
    else:
        ethernet_ipv4 = None
    # MAC ADDRESS

    # OS Release 
    os_release = platform.release()
    os_edition = platform.version()
    windows_edition = platform.win32_edition()
    windows = version = platform.system() + ' ' + platform.release()
    OS = version = platform.system()
    device_name = socket.gethostname()
    architect = platform.machine()
    # iP Address
    ip_address = socket.gethostbyname(socket.gethostname())
    Architecture = platform.architecture()
    #  Get windows name

    if request.POST:
        form = OwnerLogoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = user
            form.save()
            messages.success(request, 'Your profile has been changed successful')
            return redirect('setting', user_info.id)
        else:
            messages.error(request, 'Failed update company')
    if request.POST:
        form1 = UserForm(request.POST, instance=user)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'Your information updated successful')
            return redirect('setting', user_info.id)
        else:
            messages.error(request, 'Failed update company')
    context = {
        'profile': profile,
        'user': user,
        'OS': OS,
        'wireless_ipv4': wireless_ipv4,
        'ethernet_ipv4': ethernet_ipv4,
        'os_release': os_release,
        'os_edition': os_edition,
        'windows_edition': windows_edition,
        'windows': windows,
        'ip_address': ip_address,
        'architect': architect,
        'Architecture': Architecture,
        'device_name': device_name,
    }
    return render(request, 'setting/setting.html', context)


# ======================== Add Company Address ==================


def add_company_address(request, pk):
    countryList = Country.objects.all().order_by('-id')
    provinceList = Province.objects.all().order_by('-id')
    districtList = District.objects.all().order_by('-id')
    communeList = Commune.objects.all().order_by('-id')
    villageList = Village.objects.all().order_by('-id')
    company = Company.objects.get(id=pk)
    try:
        company_address = CompanyAddress.objects.get(company=pk)
    except CompanyAddress.DoesNotExist:
        company_address = None
    if request.POST:
        name = request.POST['name']
        house_number = request.POST['house_number']
        country_id = request.POST['country']
        country = Country.objects.get(id=country_id)
        province_id = request.POST['province']
        province = Province.objects.get(id=province_id)
        district_id = request.POST['district']
        district = District.objects.get(id=district_id)
        commune_id = request.POST['commune']
        commune = Commune.objects.get(id=commune_id)
        village_id = request.POST['village']
        village = Village.objects.get(id=village_id)
        location = request.POST['location']
        address_company = CompanyAddress(name=name, house_number=house_number, country=country,
                                         province=province, district=district, commune=commune,
                                         village=village, location=location, company=Company.objects.get(id=pk))
        address_company.save()
        return redirect('update_company', company.id)
    context = {'company_address': company_address,
               'districtList': districtList,
               'communeList': communeList,
               'provinceList': provinceList,
               'villageList': villageList,
               'countryList': countryList}
    return render(request, 'admin-company/company_address.html', context)


# ================= update company ================

@login_required(login_url='login')
def update_company(request, pk):
    user = request.user
    company = get_object_or_404(Company, id=pk)
    bank_form = BankAccountForm()
    company_id = Company.objects.get(owner=user)
    bank_account = BankAccount.objects.filter(company=company.id)
    investor = Investor.objects.filter(company=company.id)
    try:
        address_company = CompanyAddress.objects.get(company=pk)
    except CompanyAddress.DoesNotExist:
        address_company = None
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form = form.save(commit=False)
            form.owner = user
            form.save()
            messages.success(request, 'Company information updated successful')
            return redirect('update_company', pk)
        else:
            messages.error(request, 'Failed updated company')
    context = {'companyDetail': company, 'investor': investor, 'address_company': address_company, 'bank_account': bank_account}
    return render(request, 'admin-company/company-form.html', context)


@login_required
def layout(request, pk):
    user = request.user
    company = get_object_or_404(Company, id=pk)
    bank_form = BankAccountForm()
    company_id = Company.objects.get(owner=user)
    user_setting, created = Usersetting.objects.get_or_create(company=company)
    
    if request.method == 'POST':
        # Update the user_setting object and save changes
        sidebar = request.POST.get('is_sidebar', False)
        user_setting.is_sidebar = sidebar == 'on'
        user_setting.save()
        messages.success(request, 'You have updated the layout')
        return redirect('layout', pk)
    
    context = {
        'user_setting': user_setting
        }
    return render(request, 'setting/layout.html', context)


# ======================= delete bank account ==============


def deleted_bank_account(request, pk):
    bank_account = BankAccount.objects.get(id=pk)
    bank_account.delete()
    return redirect('update_company', 1)


# ================= update company  address ===============


def update_address_company(request, pk):
    countryList = Country.objects.all().order_by('-id')
    provinceList = Province.objects.all().order_by('-id')
    districtList = District.objects.all().order_by('-id')
    communeList = Commune.objects.all().order_by('-id')
    villageList = Village.objects.all().order_by('-id')
    cmp_address_update = CompanyAddress.objects.get(id=pk)
    if request.method == 'POST':
        form = CustomerFormAddress(request.POST, instance=cmp_address_update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Update company successfully!')
            return redirect('update_address_company', cmp_address_update.id)
        else:
            messages.error(request, 'Failed update company')
    context = {'cmp_address_update': cmp_address_update,
               'countryList': countryList, 'provinceList': provinceList,
               'districtList': districtList, 'communeList': communeList,
               'villageList': villageList}
    return render(request, 'admin-company/company_address.html', context)


# ============== create bank account ==============
@login_required(login_url='login')
def create_bank_account(request, pk):
    company = Company.objects.get(id=pk)
    form = BankAccountForm()
    if request.method == 'POST':
        bank_name = request.POST['bank_name']
        bank_account_name = request.POST['bank_account_name']
        bank_account_number = request.POST['bank_account_number']
        bank_account_currency = request.POST['bank_account_currency']
        form = BankAccount(bank_name=bank_name,
                           bank_account_name=bank_account_name,
                           bank_account_number=bank_account_number,
                           bank_account_currency=bank_account_currency,
                           company=Company.objects.get(id=pk))
        form.save()
        messages.success(request, 'Company bank account has been add')
        return redirect('update_company', pk)
    context = {'form': form, 'companyDetail': company}
    return render(request, 'admin-company/bank_account_form.html', context)


# =================== update back account ============
@login_required(login_url='login')
def update_bank_account(request, pk):
    bankDetail = BankAccount.objects.get(id=pk)
    company_id = bankDetail.company.id
    # company = Company.objects.get(id=company_id)
    form = BankAccountForm(instance=bankDetail)
    if request.method == 'POST':
        bankDetail.bank_name = request.POST['bank_name']
        bankDetail.bank_account_name = request.POST['bank_account_name']
        bankDetail.bank_account_number = request.POST['bank_account_number']
        bankDetail.bank_account_currency = request.POST['bank_account_currency']
        bankDetail.save()
        messages.success(request, 'Company bank account has been changed')
        return redirect('update_bank_account', company_id)
    context = {'bankAccountDetail': bankDetail, 'form': form, 'company_id': company_id}
    return render(request, 'admin-company/bank_account_form.html', context)


# PAGE NOT FOUND
def error_404_view(request, exception):
    # we add the path to the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')


# ================================ paw list ========================================


def pawList(request):
    pawList = Paw.objects.all().order_by('-id')
    paw_filter = PawFilter(request.GET, queryset=pawList)
    pawData = paw_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(pawData, 8)
    try:
        pawData = paginator.page(page)
    except PageNotAnInteger:
        pawData = paginator.page(1)
    except EmptyPage:
        pawData = paginator.page(paginator.num_pages)

    total_paw_list = Paw.objects.count()
    context = {'pawList': pawList, 'total_paw_list': total_paw_list,
               'paginator': paginator,
               'pawData': pawData}
    return render(request, 'dashboard/paw/paw_list.html', context)


def load_more(request):
    loaded_item = int(request.GET.get('loaded_item'))
    limit = 3
    pawList = list(Paw.objects.values()[loaded_item:loaded_item + limit])
    data = {'pawList': pawList}
    return JsonResponse(data=data)


# ===================== create paw using customer =======================
def pawCreate(request, pk):
    customerId = Customer.objects.get(id=pk)
    today = date.today()
    # paw_borrow = PawBorrow
    if request.method == 'POST':
        # paw_status = request.POST['paw_status']
        # paw_pay_method = request.POST['paw_pay_method']
        paw_name = request.POST['paw_name']
        description = request.POST['description']
        # paw_type = request.POST['paw_type']
        # percentage = request.POST.get('is_percentage', False)
        # principle = request.POST.get('is_principle', False)
        # is_percentage = percentage == 'on'
        # rate = request.POST['rate']
        # date_paw = request.POST['date_paw']
        # date_expired_paw = request.POST['date_expired_paw']
        paw_image = request.FILES['paw_image']
        form = Paw(customer=customerId, paw_name=paw_name, description=description,
                   paw_image=paw_image)
        form.save()
        return redirect('customer-detail', customerId.id)
    return render(request, 'dashboard/paw/paw_form_create_update.html', {'today': today, 'customerId': customerId})


# ==================== paw update ====================
def paw_update(request, pk):
    updatePaw = Paw.objects.get(id=pk)
    # pawSchedule = paw_schedule(updatePaw)
    paw = get_object_or_404(Paw, id=pk)
    customer_id = updatePaw.customer_id
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        # paw.paw_status = request.POST['paw_status']
        # paw.paw_pay_method = request.POST['paw_pay_method']
        paw.paw_name = request.POST['paw_name']
        paw.description = request.POST['description']
        if 'paw_image' in request.FILES:
            paw.paw_image = request.FILES['paw_image']
        paw.save()
        messages.success(request, "update ok")
        return redirect('paw_detail', paw.id)
    context = {'updatePaw': updatePaw}
    return render(request, 'dashboard/paw/paw_form_create_update.html', context)


# ================== Paw Detail ===================


def paw_detail(request, pk):
    pawDetail = Paw.objects.get(id=pk)
    pawOwner = pawDetail.customer
    today = date.today()
    pawBorrow = PawBorrow.objects.filter(paw=pk).order_by('-id')
    pawDetailData = []
    for pawItem in pawBorrow:
        paw_borrow_status = pawItem.paw_borrow_status
        paw_borrow_method = pawItem.paw_borrow_method
        paw_borrow_value = pawItem.paw_borrow_value
        paw_borrow_type = pawItem.paw_borrow_type
        is_percentage = pawItem.is_percentage
        borrow_rate = pawItem.borrow_rate
        is_principle = pawItem.is_principle
        paw_borrow_principle_cycle = pawItem.paw_borrow_principle_cycle
        paw_borrow_period_principle = pawItem.paw_borrow_period_principle
        date_borrow = pawItem.date_borrow
        date_expired_borrow = pawItem.date_expired_borrow
        paw_name = pawDetail.paw_name
        paw_description = pawDetail.description
        pawPay = Borrowpayback.objects.filter(borrow=pawItem.id)
        pawDetailData.append({
            'number': 1,
            'id': pawItem.id,
            'paw_borrow_status': paw_borrow_status,
            'paw_borrow_method': paw_borrow_method,
            'total_period': int(paw_borrow_principle_cycle * paw_borrow_period_principle),
            'paw_borrow_value': paw_borrow_value,
            'paw_borrow_type': paw_borrow_type,
            'is_percentage': is_percentage,
            'borrow_rate': borrow_rate,
            'is_principle': is_principle,
            'pawPay': pawPay.count(),
            'paw_borrow_principle_cycle': paw_borrow_principle_cycle,
            'paw_borrow_period_principle': paw_borrow_period_principle,
            'date_borrow': date_borrow,
            'date_expired_borrow': date_expired_borrow,
            'paw_name': paw_name,
            'paw_description': paw_description,
        })
    sumBorrow = sum(i.paw_borrow_value for i in pawBorrow)
    payBackBorrow = Borrowpayback.objects.filter(borrow__paw=pk)
    sumpayBackBorrow = sum(i.total_pay for i in payBackBorrow)
    payPaw = PawPay.objects.filter(paw=pk)
    if pawDetail.is_percentage:
        data_rate = pawDetail.paw_value * (pawDetail.rate / 100)
    else:
        data_rate = pawDetail.rate
    if request.method == 'POST':
        pay_value = request.POST['pay_value']
        date_pay = request.POST['date_pay']
        attached_file = request.FILES.get('attached_file', False)
        paw_payForm = PawPay(paw=pawDetail,
                             pay_value=pay_value,
                             date_pay=date_pay,
                             attached_file=attached_file)
        paw_payForm.save()
        return redirect('paw_detail', pawDetail.id, )
    context = {'pawDetail': pawDetail, 'payPaw': payPaw, 'today': today,
               'data_rate': data_rate, 'pawOwner': pawOwner,
               'pawDetailData': pawDetailData,
               'sumpayBackBorrow': sumpayBackBorrow,
               'payBackBorrow': payBackBorrow,
               'pawBorrow': pawBorrow, 'sumBorrow': sumBorrow}
    return render(request, 'dashboard/paw/paw_detail.html', context)


# ======================== Deleted =======================

def delete_paw(request, pk):
    pawData = Paw.objects.get(id=pk)
    if request.method == 'POST':
        Paw.objects.get(id=pk).delete()
        return redirect('paw')

    context = {'pawData': pawData}
    return render(request, 'dashboard/paw/paw_detail.html', context)


# ================================   borrow detail ======================
def create_paw_borrow(request, pk):
    paw = Paw.objects.get(id=pk)
    customerId = Customer.objects.get(id=paw.customer.id)
    today = date.today()
    if request.method == 'POST':
        paw_borrow_value = request.POST['paw_borrow_value']
        paw_borrow_method = request.POST['paw_borrow_method']
        percentage = request.POST.get('is_principle', False)
        is_percentage = percentage == 'on'
        borrow_rate = request.POST['borrow_rate']
        principle = request.POST.get('is_principle', False)
        is_principle = principle == 'on'
        paw_borrow_principle_cycle = request.POST['paw_borrow_principle_cycle']
        paw_borrow_period_principle = request.POST['paw_borrow_period_principle']
        date_borrow = request.POST['date_borrow']
        borrow_form = PawBorrow(paw=Paw.objects.get(id=pk), paw_borrow_method=paw_borrow_method,
                                paw_borrow_value=paw_borrow_value,
                                is_percentage=is_percentage, borrow_rate=borrow_rate, is_principle=is_principle,
                                paw_borrow_principle_cycle=paw_borrow_principle_cycle,
                                paw_borrow_period_principle=paw_borrow_period_principle,
                                date_borrow=date_borrow)
        borrow_form.save()
        messages.success(request, 'You create borrow successful')
        return redirect('paw_detail', pk)
    context = {'customerId': customerId, 'paw': paw, 'today': today}
    return render(request, 'dashboard/paw/borrow/create_paw_borrow.html', context)


# ========================= Borrow ===========================


def update_paw_borrow(request, pk):
    paw_Borrow_Detail = get_object_or_404(PawBorrow, id=pk)
    pawBorrowDetail = PawBorrow.objects.get(id=pk)
    paw = Paw.objects.get(id=pawBorrowDetail.paw.id)
    customer = Customer.objects.get(id=paw.customer_id)
    pawBorrowPay = Borrowpayback.objects.filter(borrow=pawBorrowDetail)
    if request.method == 'POST':
        pawBorrowDetail.paw_borrow_status = request.POST['paw_borrow_status']
        pawBorrowDetail.paw_borrow_method = request.POST['paw_borrow_method']
        pawBorrowDetail.paw_borrow_value = request.POST['paw_borrow_value']
        is_percentage = request.POST.get('is_percentage', False)
        pawBorrowDetail.is_percentage = is_percentage == 'on'
        pawBorrowDetail.borrow_rate = request.POST['borrow_rate']
        principle = request.POST.get('is_principle', False)
        pawBorrowDetail.is_principle = principle == 'on'
        pawBorrowDetail.paw_borrow_principle_cycle = request.POST['paw_borrow_principle_cycle']
        pawBorrowDetail.paw_borrow_period_principle = request.POST['paw_borrow_period_principle']
        pawBorrowDetail.date_borrow = request.POST['date_borrow']
        pawBorrowDetail.save()
        # ================ Not Update if have payment well be delete auto ===================
        return redirect('paw_borrow_detail', paw_Borrow_Detail.id)
    context = {'pawBorrowUpdate': paw_Borrow_Detail, 'paw': paw, 'customerId': customer, 'pawBorrowPay': pawBorrowPay}
    return render(request, 'dashboard/paw/borrow/create_paw_borrow.html', context)


def delete_paw_borrow(request, pk):
    pawBorrowDetail = PawBorrow.objects.get(id=pk)
    pawBorrowPay = Borrowpayback.objects.filter(borrow=pawBorrowDetail)
    pawBorrowPay.delete()
    return redirect('update_paw_borrow', pawBorrowDetail.id)

def paw_pay(request, pk):
    pawDetail = Paw.objects.get(id=pk)
    paw_pay = PawPay.objects.filter(paw=pk)
    print(paw_pay)
    context = {'pawDetail': pawDetail, 'paw': pawDetail, 'paw_pay': paw_pay}
    return render(request, 'dashboard/paw/paw_pay.html', context)

def paw_borrow_detail(request, pk):
    paw_borrow = PawBorrow.objects.get(id=pk)
    bank_account = BankAccount.objects.all()
    pay_borrow = Borrowpayback.objects.filter(borrow=paw_borrow.id)
    paw = Paw.objects.get(id=paw_borrow.paw.id)
    schedule = paw_borrow_schedule(paw_borrow)
    today = date.today()
    total_rate = sum(i['interest_rate'] for i in schedule)
    total_principle_data = sum(i['principle_data'] for i in schedule)
    total_rate_data = sum(i['paw_rate'] for i in schedule)
    total_payment_data = sum(i['payment'] for i in schedule)
    pawMigrate = []

    for i in schedule:
        pay_principle = 0
        total_pay = 0
        paid_data = []
        have_paid_status = False
        for item in pay_borrow:
            pay_principle = item.pay_principle
            total_pay = item.total_pay
            date_payback = item.date_payback
            paid_data.append({
                'pay_principle': pay_principle,
                'total_pay': total_pay,
                'date_payback': date_payback,
            })
            if i['principle_data'] == pay_principle and i['payment'] == total_pay and i['date'] == date_payback:
                have_paid_status = True
        pawMigrate.append({
            'number': i['number'],
            'paw_status': i['paw_status'],
            'principle_data': i['principle_data'],
            'paw_borrow_value': i['paw_borrow_value'],
            'is_percentage': i['is_percentage'],
            'paw_rate': i['paw_rate'],
            'interest_rate': i['interest_rate'],
            'paw_pay_method': i['paw_pay_method'],
            'payment': i['payment'],
            'pay_status': i['pay_status'],
            'percentage': i['percentage'],
            'date': i['date'],
            'have_paid_status': have_paid_status
        })
        print(pawMigrate)
    if paw_borrow.is_percentage:
        rate = int(paw_borrow.paw_borrow_value * paw_borrow.borrow_rate) / 100
    else:
        rate = paw_borrow.borrow_rate

    sum_pay_back = sum(i.total_pay for i in pay_borrow)
    if paw_borrow.is_principle:

        # ============= Payback ================================

        if request.method == 'POST':
            pay_rate = request.POST['pay_rate']
            pay_principle = request.POST['pay_principle']
            total_pay = Decimal(pay_rate) + Decimal(pay_principle)
            date_payback = request.POST['date_payback']
            borrowPay = Borrowpayback(borrow=PawBorrow.objects.get(id=pk), pay_rate=pay_rate,
                                      pay_principle=pay_principle, total_pay=total_pay,
                                      date_payback=date_payback)
            borrowPay.save()
            return redirect('paw_borrow_detail', paw_borrow.id)
    else:
        # ================================ Payback Borrow ===========================
        if request.method == 'POST':
            pay_rate = request.POST['pay_rate']
            pay_principle = 0
            total_pay = Decimal(pay_rate) + pay_principle
            date_payback = request.POST['date_payback']
            payBorrow = Borrowpayback(borrow=PawBorrow.objects.get(id=pk), pay_rate=pay_rate,
                                      pay_principle=pay_principle, total_pay=total_pay,
                                      date_payback=date_payback)
            payBorrow.save()
            return redirect('paw_borrow_detail', paw_borrow.id)
    total_date = int(paw_borrow.paw_borrow_period_principle * paw_borrow.paw_borrow_principle_cycle)

    context = {
        'schedule': schedule,
        'paw': paw,
        'paw_borrow': paw_borrow,
        'total_rate_data': total_rate_data,
        'total_payment_data': total_payment_data,
        'total_date': total_date,
        'total_principle_data': total_principle_data,
        'count_payback': schedule.count,
        'total_rate': total_rate,
        'bank_account': bank_account,
        'pay_borrow': pay_borrow,
        'today': today,
        'rate': rate,
        'sum_pay_back': sum_pay_back,
        'pay_count': pay_borrow.count(),
        'pawMigrate': pawMigrate,
    }
    return render(request, 'dashboard/paw/borrow/borrow_detail.html', context)


def paw_pay_detail(request, pk):
    pwa_Pay = PawPay.objects.get(id=pk)
    pawDetail = Paw.objects.get(id=pwa_Pay.paw.id)
    context = {'pwapay': pwa_Pay, 'pawDetail': pawDetail}
    return render(request, 'dashboard/paw/pay_paw_detail.html', context)


def refund_paw(request, pk):
    updatePaw = Paw.objects.get(id=pk)
    if request.method == 'POST':
        Paw(id=updatePaw.id, customer=updatePaw.customer, paw_status='refunded',
            paw_pay_method=updatePaw.paw_pay_method,
            paw_name=updatePaw.paw_name, paw_value=updatePaw.paw_value, description=updatePaw.description,
            paw_type=updatePaw.paw_type,
            is_percentage=updatePaw.is_percentage, rate=updatePaw.rate, date_paw=updatePaw.date_paw,
            date_expired_paw=updatePaw.date_expired_paw, paw_image=updatePaw.paw_image).save()
        return redirect('paw_detail', updatePaw.id)
    context = {'updatePaw': updatePaw}
    return render(request, 'dashboard/paw/refund_data.html', context)


def print_paw(request, pk):
    pawDetail = Paw.objects.get(id=pk)
    # pwa_Pay = PawPay.objects.get(id=pk)
    context = {'pawDetail': pawDetail}
    return render(request, 'dashboard/paw/print_paw_customer.html', context)


# ======================= search paw ==================
def searchPaw(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        dataList = request.POST.get('dataList')
        query_se = Paw.objects.filter(Q(paw_name__icontains=dataList) |
                                      Q(paw_value__icontains=dataList) |
                                      Q(paw_status__icontains=dataList) |
                                      Q(customer__name__icontains=dataList) |
                                      Q(customer__name_kh__icontains=dataList)
                                      )

        if len(query_se) > 0 and len(dataList) > 0:
            data = []
            for i in query_se:
                item = {
                    'id': i.id,
                    'name': i.paw_name,
                    'image': i.paw_image.url if i.paw_image else '',
                    'status': i.paw_status
                }
                data.append(item)
            res = data
        else:
            res = 'No paw found with what name'
        return JsonResponse({'data': res})
    return JsonResponse({})


# ========================== search payment ==============
def searchPayment(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        res = None
        paymentList = request.POST.get('paymentList')
        query_pay = Payback.objects.filter(
            Q(customer__name_kh__icontains=paymentList) |
            Q(customer__name__icontains=paymentList) |
            Q(loan__loan_number_id__icontains=paymentList) |
            Q(balance__icontains=paymentList) |
            Q(interest_paid__icontains=paymentList)
        )
        if len(query_pay) > 0 and len(paymentList) > 0:
            payData = []
            for i in query_pay:
                print(i)
                item = {
                    'id': i.id,
                    'customer_kh': i.customer.name_kh,
                    'customer': i.customer.name,
                    'loan_id': i.loan.loan_number_id,
                    'balance': i.balance,

                }
                payData.append(item)
                res = payData
        else:
            res = 'No cusomer name found with what name'
        return JsonResponse({'data': res})
    return JsonResponse({})


def employee_list(request):
    emp_list = EmployeeList.objects.all()
    context = {'emp_list': emp_list}
    return render(request, 'user/employee/employee_list.html', context)


def create_employee_detail(request):
    group = Group.objects.all()
    country = Country.objects.all()
    province = Province.objects.all()
    district = District.objects.all()
    commune = Commune.objects.all()
    village = Village.objects.all()
    position = Position.objects.all()
    department = Department.objects.all()
    if request.method == 'POST':
        user = request.POST['']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        position = request.POST['position']
        department = request.POST['department']
        profile = request.POST['']
        street = request.POST['street']
        country = request.POST['country']
        province = request.POST['province']
        district = request.POST['district']
        commune = request.POST['commune']
        village = request.POST['village']
        gender = request.POST['gender']
        birth_date = request.POST['birth_date']
        phone = request.POST['phone']
        email = request.POST['email']
    context = {
        'country': country,
        'province': province,
        'district': district,
        'commune': commune,
        'village': village,
        'position': position,
        'department': department,
        'group': group
    }
    return render(request, 'user/employee/create_employee.html', context)


def position(request):
    positionList = Position.objects.all().order_by('-id')
    position_filter = PositionFilter(request.GET, queryset=positionList)
    positions = position_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(positions, 7)
    try:
        positions = paginator.page(page)
    except PageNotAnInteger:
        positions = paginator.page(paginator.num_pages)

    company = Company.objects.all()
    company_id = Company.objects.get(id=company[0].id)
    if request.method == 'POST':
        ps_name = request.POST['ps_name']
        ps_desc = request.POST['ps_desc']
        create_position = Position(company=company_id, ps_name=ps_name, ps_desc=ps_desc)
        create_position.save()
        return redirect('position')
    context = {'positionList': positionList, 'positions': positions}
    return render(request, 'user/position/position_create_detail.html', context)


def position_delete(request, pk):
    if request.method == 'POST':
        position = Position.objects.get(id=pk)
        position.delete()
        return redirect('position')


def position_update(request, pk):
    positionUpdate = Position.objects.get(id=pk)
    positionList = Position.objects.all().order_by('-id')
    position_filter = PositionFilter(request.GET, queryset=positionList)
    positions = position_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(positions, 7)
    try:
        positions = paginator.page(page)
    except PageNotAnInteger:
        positions = paginator.page(paginator.num_pages)
    company = Company.objects.all()

    if request.method == 'POST':
        positionUpdate.company = Company.objects.get(id=company[0].id)
        positionUpdate.ps_name = request.POST['ps_name']
        positionUpdate.ps_desc = request.POST['ps_desc']
        positionUpdate.save()

    company = Company.objects.all()
    company_id = Company.objects.get(id=company[0].id)
    context = {'positionUpdate': positionUpdate,  'positions': positions}
    return render(request, 'user/position/position_create_detail.html', context)


def department(request):
    departmentList = Department.objects.all().order_by('-id')
    department_filter = DepartmentFilter(request.GET, queryset=departmentList)
    departments = department_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(departments, 7)
    company = Company.objects.all()
    company_id = Company.objects.get(id=company[0].id)
    try:
        departments = paginator.page(page)
    except PageNotAnInteger:
        departments = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        dep_name = request.POST['dep_name']
        dep_desc = request.POST['dep_desc']
        create_department = Department(company=company_id, dep_name=dep_name, dep_desc=dep_desc)
        create_department.save()
        return redirect('department')

    context = {'departments': departments}
    return render(request, 'user/department/department_create_detail.html', context)

def department_update(request, pk):
    departmentUpdate = Department.objects.get(id=pk)
    departmentList = Department.objects.all().order_by('-id')
    department_filter = DepartmentFilter(request.GET, queryset=departmentList)
    departments = department_filter.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(departments, 7)
    company = Company.objects.all()
    company_id = Company.objects.get(id=company[0].id)
    try:
        departments = paginator.page(page)
    except PageNotAnInteger:
        departments = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        departmentUpdate.dep_name = request.POST['dep_name']
        departmentUpdate.dep_desc = request.POST['dep_desc']
        departmentUpdate.save()
        return redirect('department_update', departmentUpdate.id)

    context = {'departmentUpdate': departmentUpdate,
               'departments': departments}
    return render(request, 'user/department/department_create_detail.html', context)

def department_delete(request, pk):
    department = Department.objects.get(id=pk)
    if request.method == 'POST':
        department = Department.objects.get(id=pk)
        department.delete()
        return redirect('department')

def investor(request, pk):
    context = {}
    if request.method == 'POST':
        pass
    return render(request, 'investor/create_investor.html', context)
