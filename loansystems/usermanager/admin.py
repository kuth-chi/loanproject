from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission


# Register your models here.
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'codename']

admin.site.register(Permission, PermissionAdmin)
admin.site.register(Collateral)
admin.site.register(ImageCollateral)
admin.site.register(LoanPaymentReceipt)
admin.site.register(Loan)
admin.site.register(AmortizationSchedule)
admin.site.register(Country)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Commune)
admin.site.register(Village)
admin.site.register(Payback)
admin.site.register(IdCard)
admin.site.register(imageIdCard)
admin.site.register(Activity)
admin.site.register(BankAccount)
admin.site.register(EmployeeList)
admin.site.register(PawBorrow)
admin.site.register(EmployeeDetail)
admin.site.register(Department)
admin.site.register(Position)

# For COMPANY on Admin
admin.site.register(Company)
admin.site.register(OwnerLogo)
admin.site.register(Paw)
admin.site.register(pawImage)
admin.site.register(Borrowpayback)
admin.site.register(Usersetting)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "founded")
    list_filter = ('owner', "country")

# Company Address on admin interface


class CompanyAddressAdmin(admin.ModelAdmin):
    model = CompanyAddress
    fields = ("company", "country", "province", "district", "commune", "village", "is_head_office")
    list_filter = ('company', "country", "province", "district", "commune", "village")
    list_editable = ("is_head_office",)


admin.site.register(CompanyAddress)

# Customer Address on admin interface
admin.site.register(CustomerAddress)


class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("name","customer","country", "province", "district", "commune", "village")


# Customer Shipping Address on admin interface
admin.site.register(CustomerShippingAddress)


class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("customer","country", "province", "district", "commune", "village")


# Customer on Admin interface
admin.site.register(Customer)
admin.site.register(PawPay)


class CustomerAdmin(admin.ModelAdmin):
    fields = ('name', 'gender')
    list_display = ("name", "gender", "phone", "is_black_list")
    list_editable = ("is_black_list",)
    list_display = ('upper_case_name',)

