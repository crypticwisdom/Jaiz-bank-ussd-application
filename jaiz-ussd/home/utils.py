import decimal
import uuid
import requests
from django.utils import timezone
import base64
from . import responses
from .models import *
from .api import *
from cryptography.fernet import Fernet

# def perform_bvn_check(bvn):
#     return True


def reformat_msisdn(msisdn):
    return f"0{msisdn[-10:]}"


def log_errors(err):
    logging.error(err)


def encrypt_text(text: str):
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])
    fernet = Fernet(key)
    secure = fernet.encrypt(f"{text}".encode())
    return secure.decode()


def decrypt_text(text: str):
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])
    fernet = Fernet(key)
    decrypt = fernet.decrypt(text.encode())
    return decrypt.decode()


def check_card_no(customer, text):
    # API to check customer card should be here
    # if CustomerAccount.objects.filter(card=decrypt_text(text), customer=customer).exists():
    if CustomerAccount.objects.filter(card=text, customer=customer).exists():
        return True
    else:
        return False


def send_token_to_customer(customer, remark):
    customer_otp_obj, created = CustomerOTP.objects.get_or_create(customer=customer)
    customer_otp_obj.otp = str(uuid.uuid4().int)[:4]
    customer_otp_obj.save()

    phone_number = customer.msisdn
    message = f'Kindly use the Token: {customer_otp_obj.otp} to complete {remark}'
    send_sms(phone_number, message)

    return True


def create_new_bank_customer(customer, session):
    # THIS FUNCTION CALL JAIZ BANK API TO CREATE NEW CUSTOMER ACCOUNT
    phone_no = customer.msisdn
    bvn = decrypt_text(customer.bvn)
    response = open_acct_with_bvn(phone_no, bvn)
    if response['responseCode'] != "00" or response['responseCode'] is None:
        close_session(session)

    account_no = response['acctNo']
    # CREATE CUSTOMER_ACCOUNT INSTANCE FOR NEW CUSTOMER
    CustomerAccount.objects.create(customer=customer, account_no=account_no, position=1)
    return account_no


def perform_checks(request, session_id):
    data = request.GET
    success = False
    detail = ''
    # CHECK IF NO MSISDN, NETWORK AND SESSION_ID IS SENT
    if not data.get('network') or not data.get('msisdn'):
        detail = 'msisdn and network are required parameters'
        return success, None, detail

    if Session.objects.filter(session_id=session_id).exists():
        old_session = Session.objects.get(session_id=session_id)
        if old_session.msisdn != data.get('msisdn'):
            detail = 'Session already created by another user'
            return success, None, detail

    # CHECK IF SESSION ID EXIST, OR CREATE NEW
    session, created = Session.objects.get_or_create(session_id=session_id)
    session.network = data.get('network')
    session.msisdn = data.get('msisdn')
    session.save()

    # CHECK IF SESSION_ID IS EXPIRED
    if session.expired is True or session.end_time:
        detail = 'Session has expired'
        return success, None, detail

    return True, session, detail


# FUNCTION TO CLOSE SESSION
def close_session(session):
    session.end_time = timezone.datetime.now()
    session.expired = True
    session.save()


def send_response(port, msisdn, text, session_id, message):
    url = f'http://ussdconnectorserver:{port}?msisdn={msisdn}&input={text}&sessionid={session_id}&message={message}'
    message_length = len(str(message))
    log_request(url, f"message_length: {message_length}")
    return True


def acct_bals_check_for_airtime_self(fake_acct_bals, airtime_instance, network, port, msisdn, text, session, session_id):
    """Check if customer has sufficient funds for transaction.
    """
    if decimal.Decimal(fake_acct_bals) > decimal.Decimal(airtime_instance.amount):

        # Auto-detect MNO (For Airtime-Self MNO has been given)

        if network:
            airtime_instance.network = network
            airtime_instance.save()

            message = responses.confirm_ussd_for_airtime_self(airtime_instance.customer.msisdn, network, airtime_instance.amount)
            session.current_screen = "confirm_ussd_for_airtime_self"
            session.save()
        else:
            # Manually Select Network
            message = responses.select_service_provider()
            session.current_screen = "select_service_provider"
            session.save()
    else:
        message = responses.no_sufficient_funds()
        session.current_screen = "no_sufficient_funds"
        # End Session and Update Airtime Instance status field to failed.
        airtime_instance.status = "failed"
        airtime_instance.save()
        close_session(session)

    send_response(port, msisdn, text, session_id, message)
    return message


# FUNCTION TO INCREASE PIN CHANGE TRY COUNT
def increase_change_count(customer):
    customer_pin = CustomerPin.objects.get(customer=customer)
    customer_pin.change_count += 1
    customer_pin.save()


# FUNCTION RESET PIN CHANGE TRY COUNT TO ZERO
def reset_pin_change_count(customer):
    customer_pin = CustomerPin.objects.get(customer=customer)
    customer_pin.change_count = 0
    customer_pin.save()


# USED TO EMPTY THE TEMPORALLIST MODEL
def empty_temporal_list():
    try:
        obj = TemporalList.objects.all()
        obj.delete()
    except:
        "Nothing to return"


# Select Beneficiary for Jaiz transfer
def select_beneficiary(response, beneficiary_obj):
    store_beneficiary = dict()
    name_list = []
    counter = 1
    for name in beneficiary_obj:
        name_list.append(f"{counter}.    {name.last_name} {name.first_name}\n")
        store_beneficiary[f"{counter}"] = f"{name.last_name} {name.first_name}\n"
        counter += 1

    response['message'] = f"Select Beneficiary\n{''.join(name_list)}"
    return response, store_beneficiary


def get_customer_beneficiary(customer, recipient_acct_no):
    try:
        beneficiary = customer.beneficiaries.filter(account_no=recipient_acct_no)
        return beneficiary
    except Exception as err:
        return None


def update_bill_categories():
    category = get_biller_category()
    for cat in category:
        cat_instance, _ = BillCategory.objects.get_or_create(uid=cat['ID'])
        cat_instance.name = cat['Name']
        cat_instance.description = cat['Description']
        cat_instance.save()
    return True


def update_packages():
    cats = [cat for cat in BillCategory.objects.all()]
    for obj in cats:
        package = get_biller_category_by_id(obj.uid)
        for items in package['BillItems']:
            package_instance, _ = Package.objects.get_or_create(biller_id=items['billerID'])
            package_instance.category = obj
            package_instance.name = items['Name']
            package_instance.save()
    return True


def update_items():
    biller_ids = [item.biller_id for item in Package.objects.all()]
    for ids in biller_ids:
        items = get_items_by_biller_id(ids)
        for item_ in items['Items']:
            item_instance, _ = Item.objects.get_or_create(name=item_['Name'])
            item_instance.biller_id = item_['BillID']
            item_instance.amount = item_['Amount']
            item_instance.payment_code = item_['PaymentCode']
            # item_instance.charges = item_['Surcharge']
            item_instance.save()
    return True


def billers_categories():
    try:
        # billers_categories_response = get_biller_category()
        billers_categories_response = [
            {
                "ID": 1, "QuickTellerCategoryId": 1, "Name": "Utility Bills",
                "Description": "Pay Utility Bills here", "Visible": "true", "PictureUrl": "null"
            },
            {
                "ID": 2, "QuickTellerCategoryId": 2, "Name": "Cable TV Bills",
                "Description": "Pay your cable TV bill here", "Visible": "true", "PictureUrl": "null"
            },
            {
                "ID": 3, "QuickTellerCategoryId": 3, "Name": "Mobile Recharge",
                "Description": "Recharge your phone", "Visible": "true", "PictureUrl": "null"
            }
        ]
        return True, billers_categories_response
    except Exception as err:
        return False, str(err)
