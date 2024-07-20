from django.contrib import admin
from . models import *


class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'msisdn', 'current_screen']
    list_filter = ['start_time', 'end_time', 'expired']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['biller_id', 'name', 'amount', 'payment_code']
    list_filter = ['status', 'created_on']


class CustomerPinInline(admin.TabularInline):
    model = CustomerPin


class CustomerOtpInline(admin.TabularInline):
    model = CustomerOTP


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['msisdn', 'first_name', 'last_name']
    search_fields = ['msisdn', ]
    inlines = [CustomerOtpInline, CustomerPinInline]


# admin.site.register(Provider)
admin.site.register(Airtime)
admin.site.register(Beneficiary)
admin.site.register(CustomerAccount)
admin.site.register(FundTransfer)
admin.site.register(CableSubscription)
admin.site.register(SessionBeneficiary)
admin.site.register(Session, SessionAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Data)
admin.site.register(TemporalList)
admin.site.register(Electricity)
admin.site.register(FundReversal)
admin.site.register(BillCategory)
admin.site.register(Package)
# admin.site.register(Item)
