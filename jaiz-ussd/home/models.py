import uuid

from django.db import models
from django.contrib.auth.models import User

from .choices import *


class Session(models.Model):
    session_id = models.CharField(max_length=500, blank=True, null=True)
    service_code = models.CharField(max_length=100, default='*773#')
    # access_code = models.CharField(max_length=100, default='')
    network = models.CharField(max_length=100, default='')
    msisdn = models.CharField(max_length=100, default='')
    # command = models.CharField(max_length=100, default='continue')
    current_screen = models.CharField(max_length=200, default='main_menu_first_page')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.session_id}'


class BillCategory(models.Model):
    uid = models.IntegerField(max_length=None)
    name = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=200, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uid}-{self.name}"

    class Meta:
        verbose_name_plural = "Bill Categories"


class Package(models.Model):
    category = models.ForeignKey(BillCategory, on_delete=models.CASCADE, null=True)
    biller_id = models.IntegerField(max_length=None)
    name = models.CharField(max_length=200, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.biller_id}-{self.name}"


class Item(models.Model):
    biller_id = models.IntegerField(default=0)
    name = models.CharField(max_length=200, default='')
    amount = models.CharField(max_length=200, default='')
    payment_code = models.CharField(max_length=200, default='')
    charges = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    # page = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class SessionBeneficiary(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    beneficiary = models.CharField(max_length=20, default='')

    def __str__(self):
        return f'{self.session.session_id} - {self.beneficiary}'


class Beneficiary(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    account_no = models.CharField(max_length=500, default='')

    def __str__(self):
        return f'{self.account_no} - {self.first_name} - {self.last_name}'

    class Meta:
        verbose_name_plural = 'Beneficiaries'


class Customer(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    # dob = models.DateTimeField(null=True, blank=True)
    dob = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='male')
    onboarded = models.BooleanField(default=False)
    msisdn = models.CharField(max_length=20)
    bvn = models.CharField(max_length=200, blank=True, null=True)
    recovery_code = models.CharField(max_length=500, blank=True, null=True)
    last_transaction_amount = models.FloatField(max_length=20, default=0.0)
    active = models.BooleanField(default=True)
    beneficiaries = models.ManyToManyField(Beneficiary, blank=True)

    def __str__(self):
        return self.msisdn


class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES, default='savings')
    account_no = models.CharField(max_length=500, default='')
    position = models.CharField(max_length=10, blank=True, null=True)
    amount = models.FloatField(max_length=20, default=0.0)
    has_card = models.BooleanField(default=False)
    card = models.CharField(max_length=500, blank=True, null=True)
    active = models.BooleanField(default=True)
    request_transaction = models.BooleanField(default=False)
    request_block = models.BooleanField(default=False)
    request_removal = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.msisdn} - {self.account_type}'

    # def save(self, *args, **kwargs):
    #     cus = self.customer
    #     if CustomerAccount.objects.filter(customer=self.customer).count() == 0:
    #         print("He exist")
    #     else:
    #         print("Does not exist")
    #     return


class CustomerPin(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    pin = models.CharField(max_length=500, default='')
    last_pin = models.CharField(max_length=500, blank=True, null=True)
    prev_pin = models.CharField(max_length=500, blank=True, null=True)
    change_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.msisdn}'


class CustomerOTP(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f'{self.customer}-{self.otp}'


class Airtime(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.SET_NULL, null=True)
    purchase_type = models.CharField(max_length=20, choices=AIRTIME_PURCHASE_TYPE, default='self')
    amount = models.FloatField(max_length=20, default=0.0)
    beneficiary = models.CharField(max_length=20, null=True, blank=True)
    network = models.CharField(max_length=20, default='MTN')
    transaction_ref = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    pin_tries = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer} - {self.purchase_type}, {self.network} - {self.amount}'


class Data(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.SET_NULL, null=True)
    purchase_type = models.CharField(max_length=20, choices=DATA_PURCHASE_TYPE, default='self')
    amount = models.FloatField(max_length=20, default=0.0)
    beneficiary = models.CharField(max_length=20, null=True, blank=True)
    network = models.CharField(max_length=20, default='MTN')
    data_amount = models.CharField(max_length=200, blank=True, null=True)
    transaction_ref = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    pin_tries = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer} - {self.purchase_type}, {self.network} - {self.amount}'

    class Meta:
        verbose_name = "Data"
        verbose_name_plural = "Data"


class FundTransfer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField(max_length=20, default=0.0)
    transfer_type = models.CharField(max_length=20, choices=FUND_TRANSFER_TYPE, default='jaiz')
    account_no = models.CharField(max_length=500, default='')
    bank_list_response = models.JSONField(null=True)
    bank_selected = models.CharField(max_length=10, null=True)
    receiver_name = models.CharField(max_length=50, null=True, blank=True)
    bank = models.CharField(max_length=20, null=True)
    next = models.IntegerField(null=True)
    transaction_ref = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    pin_tries = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer} - {self.amount}, {self.transfer_type}'


class Electricity(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    meter_number = models.CharField(max_length=200, default='')
    payment_type = models.CharField(max_length=20, choices=ELECTRICITY_PAYMENT_TYPE, default='prepaid')
    amount = models.FloatField(max_length=20, default=0.0)
    doe = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=200, default='')
    status = models.CharField(max_length=50, choices=BILL_STATUS, default='pending')
    transaction_ref = models.CharField(max_length=250, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Electricities'

    def __str__(self):
        # return f'{self.customer} - {str(self.item.name)}, {self.meter_number} - {self.amount}'
        return f'{self.customer} - {self.meter_number} - {self.amount}'


class CableSubscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    smart_card_number = models.CharField(max_length=200, default='')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    transaction_ref = models.CharField(max_length=250, blank=True, null=True)
    subscription_type = models.CharField(max_length=20, choices=BILL_STATUS, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    next = models.IntegerField(default=1, null=True, blank=True)
    pin_tries = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return f'{self.customer} - {self.item.name}/{self.item.amount}'
        return f'{self.customer} - {self.item}/{self.item}'


# FOR STORING TEMPORARY LIST FOR SELECTION
class TemporalList(models.Model):
    num = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    account_no = models.CharField(max_length=200, null=True, default="")

    def __str__(self):
        return str(f"{self.num}. {self.name}")


class FundReversal(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    has_ran = models.BooleanField(default=False)
    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.SET_NULL, null=True)
    msisdn = models.CharField(max_length=20, null=True)
    amount = models.FloatField(max_length=20, default=0.0)
    session_id = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=200, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    beneficiary = models.CharField(max_length=20, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.transaction_type}"

# Still not sure if this model will be needed

# class BillTracker(models.Model):
#     bill_category = models.ForeignKey(BillCategory, on_delete=models.SET_NULL, null=True)
#     bill_package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
#     item_selected = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
#     amount = models.FloatField(max_length=20, default=0.0)
#     created_on = models.DateTimeField(auto_now_add=True)
#     updated_on = models.DateTimeField(auto_now=True)
