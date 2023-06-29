from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .paw_view import *
from .views import *
from .support import *

# from .views import line_chart, line_chart_json
urlpatterns = [
    path('', views.dashboard, name='index'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logoutPage, name='logout'),
    # path('restriction/', views.restriction, name='restriction'),

    # ============= User's Setting ===========================
    path('setting/<str:pk>/', views.setting, name='setting'),
    path('layout/<str:pk>/', views.layout, name='layout'),
    # ============= Company ===========================

    # ================ user ===================

    path('create_company/<str:pk>/', views.create_company, name='create_company'),
    path('update_company/<str:pk>/', views.update_company, name='update_company'),
    path('add_company_address/<str:pk>/', views.add_company_address, name='add_company_address'),
    path('update_address_company/<str:pk>/', views.update_address_company, name='update_address_company'),

    #======================= bank account =========================


    path('deleted_bank_account/<str:pk>/', views.deleted_bank_account, name='deleted_bank_account'),
    path('create_bank_account/<str:pk>/', views.create_bank_account, name='create_bank_account'),
    path('update_bank_account/<str:pk>/', views.update_bank_account, name='update_bank_account'),

    # =============== Customer =============

    path('create-loan-customer/<str:pk>/', views.create_loan_for_customer, name='create_loan_customer'),
    path('loan_detail_from_customer/<str:pk>/', views.loan_detail_from_customer, name='loan_detail_customer'),
    path('customer/', views.customer_list, name='customer'),
    path('customer-detail/<str:pk>/', views.customer_detail, name='customer-detail'),
    path('create-customer/', views.create_customer, name='create_customer'),
    path('update-customer/<str:pk>/', views.update_customer, name='update_customer'),
    path('delete-customer/<str:pk>/', views.delete_customer, name='delete_customer'),


    path('search_data/', customer_search_list.as_view(), name='search_data'),

    path('search_customer/', views.search_customer, name='search_customer'),
    path('address/', views.address, name='address'),
    path('search_customerAddress/', views.search_customerAddress, name='search_customerAddress'),

    # =============== Country ======================

    path('create-country/', views.create_county, name='create_country'),
    path('country-list/', views.country_list, name='country_list'),
    path('country-detail/<str:pk>/', views.country_detail, name='country_detail'),
    path('country-update/<str:pk>/', views.update_country, name='country_update'),
    path('delete-country/<str:pk>/', views.delete_country, name='delete_country'),

    # =========================== Province =======================

    path('create-province/', views.create_province, name='create_province'),
    path('province-list/', views.province_list, name='province_list'),
    path('province-detail/<str:pk>/', views.province_detail, name='province_detail'),
    path('province-update/<str:pk>/', views.update_province, name='province_update'),
    path('delete-province/<str:pk>/', views.delete_province, name='delete_province'),

    # ========================== District ========================

    path('create-district/', views.create_district, name='create_district'),
    path('district-list/', views.district_list, name='district_list'),
    path('district-detail/<str:pk>/', views.district_detail, name='district_detail'),
    path('district-update/<str:pk>/', views.update_district, name='district_update'),
    path('delete-district/<str:pk>/', views.delete_district, name='delete_district'),

    # ================================ Commune =========================

    path('create-commune/', views.create_commune, name='create_commune'),
    path('commune-list/', views.commune_list, name='commune_list'),
    path('commune-detail/<str:pk>/', views.commune_detail, name='commune_detail'),
    path('commune-update/<str:pk>/', views.update_commune, name='commune_update'),
    path('delete-commune/<str:pk>/', views.delete_commune, name='delete_commune'),

    # ======================================= Village =============================
    path('create-village/', views.create_village, name='create_village'),
    path('village-list/', views.village_list, name='village_list'),
    path('village-detail/<str:pk>/', views.village_detail, name='village_detail'),
    path('village-update/<str:pk>/', views.update_village, name='village_update'),
    path('delete-village/<str:pk>/', views.delete_village, name='delete_village'),

    # =========================== Customer Address =========================

    path('customer-address/<str:pk>/', views.create_customer_address, name='create_customer_address'),
    path('update-customer-address/<str:pk>/', views.update_customer_address, name='update_customer_address'),
    path('delete-customer-address/<str:pk>/', views.delete_customer_address, name='delete_customer_address'),

    # ========================= Collateral Page ==============================

    path('collateral_list/', views.collateral_list, name='collateral_list'),
    path('create_collateral/', views.create_collateral, name='create_collateral'),
    path('delete_collateral/<str:pk>/', views.delete_collateral, name='delete_collateral'),
    path('search_collateral/', views.search_collateral, name='search_collateral'),

    # ======================= Collateral with customer =================================

    path('update_collateral/<str:pk>/', views.update_collateral, name='update_collateral'),
    path('create_collateral_loan/<str:pk>/', views.create_collateral_loan, name='create_collateral_loan'),
    path('collateral_detail/<str:pk>/', views.collateral_detail, name='collateral_detail'),

    # ============== dashboard ===================

    path('dashboard/', views.dashboard, name='dashboard'),

    # ===================== Loan ========================

    path('loan-json/<str:pk>/', views.schedule_loan_json, name='loan-json'),
    path('loan/', views.loan, name='loan'),
    path('loan-create/', views.loanCreate, name='loan-create'),
    path('loan_detail/<str:pk>/', views.loan_detail, name='loan_detail'),
    path('loan_update/<str:pk>/', views.loan_update, name='loan_update'),
    path('search_loan/', views.search_loan, name='search_loan'),


    # =============== Payback ======================

    path('payback/', views.payback, name='payback'),
    path('payback_detail/<str:pk>/', views.payback_detail, name='payback_detail'),
    path('create_payback/<str:pk>/', views.create_payback, name='create_payback'),
    path('create_full_payback/<str:pk>/', views.create_full_payback, name='create_full_payback'),
    path('filter_payback_by_loan_id/<str:pk>/', views.filter_payback_by_loan_id, name='filter_payback_by_loan_id'),
    path('full_paid_pack/<str:pk>/', views.full_paid_pack, name='full_paid_pack'),

    # =========================== Report ========================

    path('view-pdf/<str:pk>/', views.view_html_pdf, name='view-print'),


    # ========================== ID CARD =========================
    path('create_id_card/<str:pk>/', views.create_id_card, name='create_id_card'),
    path('card_id_detail/<str:pk>/', views.id_card_detail, name='id_card_detail'),
    path('update_id_card/<str:pk>/', views.update_id_card, name='update_id_card'),
    path('delete_id_card/<str:pk>/', views.delete_id_card, name='delete_id_card'),

    # ========================= Report =======================
    path('over_due_date/', views.Overdue_date, name='over_due_date'),

    # ========================= Activity ==============================

    path('recent_activities/', views.recent_activities, name='recent_activities'),
    path('delete_activities/<str:pk>/', views.delete_activities, name='delete_activities'),
    path('delete_all_activities/', views.delete_all_activities, name='delete_all_activities'),


    # =========================== paw =================================
    path('paw/', views.pawList, name='paw'),
    path('paw_create/<str:pk>/', views.pawCreate, name='paw_create'),
    path('paw_update/<str:pk>/', views.paw_update, name='paw_update'),
    path('paw_detail/<str:pk>/', views.paw_detail, name='paw_detail'),
    path('delete_paw/<str:pk>/', views.delete_paw, name='delete_paw'),
    path('load_more/', views.load_more, name='load_more'),

    path('paw_pay_detail/<str:pk>/', views.paw_pay_detail, name='paw_pay_detail'),
    path('paw_pay/<str:pk>/', views.paw_pay, name='paw_pay'),
    path('refund_paw/<str:pk>/', views.refund_paw, name='refund_paw'),
    path('print_paw/<str:pk>/', views.print_paw, name='print_paw'),

    # ============================ paw borrow ==============
    path('paw_borrow_detail/<str:pk>/', views.paw_borrow_detail, name='paw_borrow_detail'),
    path('create_paw_borrow/<str:pk>/', views.create_paw_borrow, name='create_paw_borrow'),
    path('update_paw_borrow/<str:pk>/', views.update_paw_borrow, name='update_paw_borrow'),
    path('delete_paw_borrow/<str:pk>/', views.delete_paw_borrow, name='delete_paw_borrow'),

    # Change URL
    
    # Support URL
    path('support/', support, name='support'),


    # Search Paw
    path('searchPaw/', views.searchPaw, name='searchPaw'),

    path('search-payment/', views.searchPayment, name='search-payment'),
    # Employee list
    path('employee_list/', views.employee_list, name='employee_list'),
    path('create_employee_detail/', views.create_employee_detail, name='create_employee_detail'),


    #position
    path('position/', views.position, name='position'),
    path('position_update/<str:pk>/', views.position_update, name='position_update'),
    path('position_delete/<str:pk>/', views.position_delete, name='position_delete'),

    path('department/', views.department, name='department'),
    path('department_update/<str:pk>/', views.department_update, name='department_update'),
    path('department_delete/<str:pk>/', views.department_delete, name='department_delete'),

    path('investor/<str:pk>/', views.investor, name='investor'),

    ]
