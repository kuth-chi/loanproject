import calendar
import decimal
import json

from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
# CHART JS
from django.views.generic import TemplateView, ListView
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import *
import math
from django.http import JsonResponse, HttpResponse, FileResponse
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from uuid import UUID
from fpdf import FPDF
from django.conf import settings
import socket, platform, os, uuid, re, sys


def paw_borrow_schedule(paw_borrow):
    paw = Paw.objects.get(id=paw_borrow.paw.id)
    paw_name = paw.paw_name
    customer = paw.customer
    paw_value = paw.paw_value
    paw_status = paw.paw_status
    paw_pay_method = paw.paw_pay_method
    # =================== paw borrow ==============
    paw_borrow_status = paw_borrow.paw_borrow_status
    paw_pay_method = paw_borrow.paw_borrow_method
    paw_borrow_value = paw_borrow.paw_borrow_value
    paw_borrow_type = paw_borrow.paw_borrow_type
    is_percentage = paw_borrow.is_percentage
    borrow_rate = paw_borrow.borrow_rate
    is_principle = paw_borrow.is_principle
    paw_borrow_principle_cycle = paw_borrow.paw_borrow_principle_cycle
    paw_borrow_period_principle = paw_borrow.paw_borrow_period_principle
    date_borrow = paw_borrow.date_borrow
    paw_data = []
    paw_pay = PawPay.objects.filter(paw=paw.id)
    sum_paw_pay = sum(i.pay_principle for i in paw_pay)
    pay_borrow = Borrowpayback.objects.filter(borrow=paw_borrow.id)
    if is_percentage:
        paw_rate = paw_borrow_value * (Decimal(borrow_rate) / 100)
    else:
        paw_rate = borrow_rate
    if is_principle:
        data = int(paw_borrow_principle_cycle * paw_borrow_period_principle)
        principle_data = (paw_borrow_value / paw_borrow_principle_cycle)
        if is_percentage:
            interest_rate = paw_borrow_value * (borrow_rate / 100)
            percentage = borrow_rate
        else:
            interest_rate = borrow_rate
            percentage = ''
            add_principle_pay = []
        for i in range(0, data):
            if paw_pay_method == 'day':
                end_date = date_borrow + timedelta(days=i)
            elif paw_pay_method == 'week':
                end_date = date_borrow + relativedelta(weeks=+i)
            elif paw_pay_method == 'month':
                end_date = date_borrow + relativedelta(months=+i)
            elif paw_pay_method == 'year':
                end_date = date_borrow + relativedelta(years=+i)
            else:
                end_date = date_borrow
            pay_status = False
            interest_rate = math.ceil(interest_rate)
            principle_data = math.ceil(principle_data)
            for item in pay_borrow:
                if Decimal(principle_data) == Decimal(item.pay_principle):
                    have_paid = True
                else:
                    have_paid = False
            if (i + 1) % int(paw_borrow_period_principle) == 0:
                paw_data.append({
                    'number': i + 1,
                    'paw_status': paw_status,
                    'principle_data': principle_data,
                    'paw_borrow_value': paw_borrow_value,
                    'is_percentage': is_percentage,
                    'paw_rate': paw_rate,
                    'interest_rate': interest_rate,
                    'paw_pay_method': paw_pay_method,
                    'payment': math.ceil(principle_data + interest_rate),
                    'pay_status': pay_status,
                    'percentage': percentage,
                    'date': end_date,
                })
            else:
                paw_data.append({
                    'number': i + 1,
                    'paw_status': paw_status,
                    'principle_data': 0.00,
                    'paw_borrow_value': paw_borrow_value,
                    'is_percentage': is_percentage,
                    'paw_rate': paw_rate,
                    'interest_rate': interest_rate,
                    'paw_pay_method': paw_pay_method,
                    'pay_status': pay_status,
                    'payment': math.ceil(0 + interest_rate),
                    'percentage': percentage,
                    'date': end_date,
                })

        # total_interest = sum(i['interest_rate'] for i in paw_data)
            # ============= Update and change expired date data ===========
        # change_expired = Paw(id=paw.id, customer=customer, paw_value=paw_value, paw_status=paw_status,
        #                      paw_pay_method=paw_pay_method, paw_name=paw_name,
        #                      description=paw.description, paw_type=paw.paw_type, is_percentage=is_percentage,
        #                      paw_image=paw.paw_image, rate=paw.rate, date_paw=paw.date_paw,
        #                      is_principle=paw.is_principle, paw_principle_cycle=paw.paw_principle_cycle,
        #                      paw_period_principle=paw.paw_period_principle, timestamp=paw.timestamp,
        #                      date_expired_paw=paw_data[-1]['date']
        #                      )
        # change_expired.save()
    # else:
        # change_expired = Paw(id=paw.id, customer=customer, paw_value=paw_value, paw_status=paw_status,
        #                      paw_pay_method=paw_pay_method, paw_name=paw_name,
        #                      description=paw.description, paw_type=paw.paw_type, is_percentage=is_percentage,
        #                      paw_image=paw.paw_image, rate=paw.rate, date_paw=paw.date_paw,
        #                      is_principle=paw.is_principle, paw_principle_cycle=paw.paw_principle_cycle,
        #                      paw_period_principle=paw.paw_period_principle, timestamp=paw.timestamp,
        #                      date_expired_paw=paw.date_expired_paw
        #                      )
        # change_expired.save()
        # if is_percentage:
        #     paw_rate = paw_value * (paw_rate / 100)
        # else:
        #     paw_rate = paw_rate
    return paw_data
