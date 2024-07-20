from threading import Thread
from . import responses
from .models import Airtime, FundTransfer, CustomerAccount
from .utils import *
from .models import *
from .api import *
from .utils import encrypt_text, decrypt_text
from datetime import datetime


def main_menu_first_page_screen(text, session, customer):
    message = ''
    if text == "1":
        Airtime.objects.get_or_create(customer=customer, session=session, network=session.network)
        message = responses.airtime_amount_self()
        session.current_screen = 'airtime_amount_self'
        session.save()

    elif text == "2":
        message = responses.airtime_others_receiver_number()
        session.current_screen = 'airtime_others_receiver_number'
        session.save()

    elif text == "3":
        # Data.objects.get_or_create(customer=customer, session=session)
        message = responses.buy_data_type()
        session.current_screen = 'buy_data_type'
        session.save()

    elif text == "4":
        # Transfer to Jaiz Bank
        message = responses.transfer_jaiz_acct()
        session.current_screen = "transfer_jaiz_acct"
        session.save()

    elif text == "5":
        FundTransfer.objects.get_or_create(
            customer=customer,
            transfer_type='others',
            session=session, status="pending"
        )
        message = responses.transfer_jaiz_acct()  # This function was also used in Jaiz Transfer.
        session.current_screen = "others_account_number"  # This page "others_account_number" doesn't have a response.
        session.save()

    elif text == "6":
        # Pay Bills
        message = responses.pay_bills_option()
        session.current_screen = "pay_bills_option_page"
        session.save()

    elif text == "7":
        customer_account = CustomerAccount.objects.filter(customer=customer)
        message = responses.account_balance_select_acct(customer_account)
        session.current_screen = "account_balance_select_acct"
        session.save()

    elif text == "8":
        message = responses.main_menu_second_page()
        session.current_screen = 'main_menu_second_page'
        session.save()

    return message


def main_menu_second_page_screen(text, session, customer):
    message = ''
    if text == "1":
        all_customer_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
        message = responses.last_five_transactions(all_customer_accounts)
        session.current_screen = 'last_five_transactions'
        session.save()

    elif text == "2":
        message = responses.facility_balance_pin()
        session.current_screen = "facility_balance_pin"
        session.save()

    elif text == "3":
        message = "Resource is currently not available, please try again later\n\n0. Main Menu"
        session.save()

    elif text == "4":
        message = responses.change_pin_request()
        session.current_screen = 'change_pin_request'
        session.save()

    elif text == "5":
        message = responses.add_or_remove_account()
        session.current_screen = "add_or_remove_account"
        session.save()

    elif text == "6":
        message = responses.confirm_pin_to_opt_out()
        session.current_screen = "confirm_pin_to_opt_out"
        session.save()
    elif text == "7":
        message = responses.reset_pin_request()
        session.current_screen = 'reset_pin_request'
        session.save()
    elif text == "8":
        message = responses.limit_agreement()
        session.current_screen = 'limit_agreement'
        session.save()
    elif text == "9":
        all_customer_accounts = CustomerAccount.objects.filter(customer=customer)
        message = responses.block_account_request(all_customer_accounts)
        session.current_screen = 'block_account_request'
        session.save()

    return message


def open_account_with_bank_screen(customer, text, session):
    message = ''
    bvn = text
    # PERFORM BVN CHECK
    success = bvn_validation(bvn)
    if success['SearchResult']['ResultStatus'] == "00":
        # SAVE NEW USER DETAIL OBTAINED FROM BVN CHECK TO CUSTOMER TABLE
        result = success['SearchResult']['BvnSearchResult']
        customer.first_name = result['FirstName']
        customer.last_name = result['LastName']
        customer.middle_name = result['MiddleName']
        customer.dob = result['DateOfBirth']
        customer.bvn = encrypt_text(bvn)
        customer.save()
        message = responses.bvn_check_success(customer.first_name, customer.last_name, customer.dob)
        session.current_screen = 'bvn_check_success'
        session.save()
    else:
        message = responses.bvn_check_fail()
        session.current_screen = 'bvn_check_fail'
        session.save()
        close_session(session)
    return message


def bvn_check_success_screen(customer, text, session):
    if text == '1':
        # CREATE NEW CUSTOMER ACCOUNT
        account_no = create_new_bank_customer(customer, session)
        message = responses.open_account_success(account_no)
        session.current_screen = 'open_account_success'
        session.save()
    elif text == '2':
        message = 'END'
        close_session(session)
    else:
        message = responses.bvn_check_success(customer.first_name, customer.last_name, customer.dob)
        session.current_screen = 'bvn_check_success'
        session.save()
    return message


def open_account_success_screen(customer, text, session):
    customer_acct = CustomerAccount.objects.filter(customer=customer).last()
    if text == '1':
        account_no = customer_acct.account_no
        message = responses.create_new_pin_input(account_no)
        session.current_screen = 'create_new_pin_input'
        session.save()
    elif text == '2':
        message = 'END'
        # close_session(session)
    else:
        account_no = customer_acct.account_no
        message = responses.open_account_success(account_no)
        session.current_screen = 'open_account_success'
        session.save()
    return message


def create_new_pin_input_screen(customer, text, session, customer_pin):
    customer_acct = CustomerAccount.objects.filter(customer=customer).last()
    if len(text) > 4 or len(text) < 4 or str(text).isdigit() is False:
        account_no = customer_acct.account_no
        message = responses.create_new_pin_input_invalid(account_no)
        session.current_screen = 'create_new_pin_input'
        session.save()
    else:
        customer_pin.last_pin = encrypt_text(text)
        customer_pin.save()
        message = responses.create_new_pin_retype()
        session.current_screen = 'create_new_pin_retype'
        session.save()
    return message


def create_new_pin_retype_screen(customer, text, session, customer_pin):
    customer_acct = CustomerAccount.objects.filter(customer=customer).last()
    if len(text) > 4 or len(text) < 4 or text != decrypt_text(customer_pin.last_pin) or str(text).isdigit() is False:
        account_no = customer_acct.account_no
        message = responses.create_new_pin_input_invalid(account_no)
        session.current_screen = 'create_new_pin_input'
        session.save()
    else:
        customer_pin.last_pin, customer_pin.prev_pin, customer_pin.pin = encrypt_text(text), encrypt_text(text), \
                                                                         encrypt_text(text)
        customer_pin.change_count += 1
        customer_pin.save()
        customer.onboarded = True
        customer.save()
        first_name = customer.first_name
        message = responses.create_new_pin_success(first_name)
        session.current_screen = 'create_new_pin_success'
        session.save()
    return message


def onboard_customer_screen(text, session, customer):
    if text == "1":
        message = responses.enter_card_no_onboard()
        session.current_screen = 'enter_card_no_onboard'
        session.save()
    # elif text == "2":
    #     message = responses.enter_bvn_onboard()
    #     session.current_screen = 'enter_bvn_onboard'
    #     session.save()
    elif text == "2":
        # Send token to user
        Thread(target=send_token_to_customer, args=[customer, 'onboarding']).start()
        message = responses.enter_token_onboard()
        session.current_screen = 'enter_token_onboard'
        session.save()
    else:
        message = responses.onboard_customer()
        session.current_screen = 'onboard_customer'
        session.save()
    return message


def card_token_onboarding_screen(session, text, customer):
    # Perform debit card check
    if len(text) == 6:
        # Check if debit card number is correct
        success = check_card_no(customer, text)
        if success is True:
            message = responses.enter_account_no_onboard()
            session.current_screen = 'enter_account_no_onboard'
            session.save()
        else:
            message = 'END Invalid card detail'
            close_session(session)

    # Perform token check
    elif len(text) == 4:
        customer_otp = CustomerOTP.objects.get(customer=customer)
        if customer_otp.otp == text:
            message = responses.enter_account_no_onboard()
            session.current_screen = 'enter_account_no_onboard'
            session.save()
        else:
            message = 'END Token is not valid'
            close_session(session)
    # Return invalid input
    elif len(text) not in (4, 6):
        message = 'END Your input is not valid'
        close_session(session)
    return message


def enter_new_pin_onboard_screen(account_no, text, session, customer_pin):
    if len(text) > 4 or len(text) < 4 or str(text).isdigit() is False:
        message = responses.enter_new_pin_onboard_invalid(account_no)
        session.current_screen = 'enter_new_pin_onboard'
        session.save()
    else:
        # Hash pin and save
        customer_pin.last_pin = encrypt_text(text)
        customer_pin.save()
        message = responses.retype_new_pin_onboard(account_no)
        session.current_screen = 'retype_new_pin_onboard'
        session.save()
    return message


def retype_new_pin_onboard_screen(text, customer_pin, session, customer, account_no):
    success = True
    if len(text) > 4 or len(text) < 4 or str(text).isdigit() is False or decrypt_text(customer_pin.last_pin) != text:
        message = responses.enter_new_pin_onboard_invalid(account_no)
        session.current_screen = 'enter_new_pin_onboard'
        session.save()
    else:
        customer_pin.last_pin, customer_pin.prev_pin, customer_pin.pin = encrypt_text(text), encrypt_text(
            text), encrypt_text(text)
        customer_pin.change_count += 1
        customer_pin.save()
        customer.onboarded = True
        customer.active = True
        customer.save()
        first_name = customer.first_name
        message = responses.enter_new_pin_onboard_success(first_name)
        session.current_screen = 'enter_new_pin_onboard_success'
        session.save()
    return message


def last_five_transactions_screen(text, customer, session):
    if text == "*":
        message = responses.main_menu_second_page()
        session.current_screen = 'main_menu_second_page'
        session.save()
    else:
        try:
            acct = CustomerAccount.objects.get(customer=customer, position=text)
            acct.request_transaction = True
            acct.save()
            message = responses.last_five_transactions_enter_pin()
            session.current_screen = 'last_five_transactions_enter_pin'
            session.save()
        except Exception:
            message = "END Invalid input"
            close_session(session)
    return message


def change_pin_request_screen(text, session, customer_pin):
    if decrypt_text(customer_pin.pin) == text:
        message = responses.enter_new_pin_change_pin()
        session.current_screen = 'enter_new_pin_change_pin'
        session.save()
    else:
        message = "END Incorrect PIN"
        close_session(session)
    return message


def enter_new_pin_change_pin_screen(text, session, customer_pin):
    if customer_pin.pin == text:
        message = "CON New PIN cannot be the same as current PIN\n \nKindly enter new PIN"
    elif len(text) > 4 or len(text) < 4 or str(text).isdigit() is False:
        message = "CON PIN should be 4 digits\n \nKindly enter new PIN"
    else:
        customer_pin.last_pin = encrypt_text(text)
        customer_pin.save()
        message = responses.enter_new_pin_change_pin_confirm()
        session.current_screen = 'enter_new_pin_change_pin_confirm'
        session.save()
    return message


def enter_new_pin_change_pin_confirm_screen(text, session, customer_pin):
    if decrypt_text(customer_pin.last_pin) != text:
        message = "CON Invalid PIN\n \nKindly enter new PIN"
        session.current_screen = 'enter_new_pin_change_pin'
        session.save()
    else:
        customer_pin.prev_pin = encrypt_text(customer_pin.pin)
        customer_pin.pin = encrypt_text(text)
        customer_pin.change_count += 1
        customer_pin.save()
        first_name = customer_pin.customer.first_name
        message = responses.change_pin_success(first_name)
    return message


def reset_pin_request_screen(session, text, customer):
    try:
        CustomerAccount.objects.get(customer=customer, account_no=text)
        message = responses.reset_pin_enter_acct_number()
        session.current_screen = 'reset_pin_enter_acct_number'
        session.save()
    except Exception:
        message = "CON Account number not valid\n0. Main Menu"
    return message


def reset_pin_enter_acct_number_screen(text, session, customer):
    if text == "1":
        message = responses.reset_pin_enter_debit_card()
        session.current_screen = 'reset_pin_enter_debit_card'
        session.save()
    elif text == "2":
        Thread(target=send_token_to_customer, args=[customer, 'pin reset']).start()
        message = responses.reset_pin_enter_token()
        session.current_screen = 'reset_pin_enter_token'
        session.save()
    else:
        message = responses.reset_pin_enter_acct_number()
        session.current_screen = 'reset_pin_enter_acct_number'
        session.save()
    return message


def card_or_token_input_screen(customer, text, session):
    query = Customer.objects.filter(customerotp__otp=text) | Customer.objects.filter(customeraccount__card=text)
    if not query:
        message = "CON Input digits not valid\n0. Main Menu"
    else:
        message = responses.reset_pin_enter_new_pin()
        session.current_screen = 'reset_pin_enter_new_pin'
        session.save()
    return message


def reset_pin_enter_new_pin_screen(text, customer_pin, session):
    if len(text) != 4 or str(text).isdigit() is False:
        message = "CON Invalid PIN, enter new PIN\n\n0. Cancel"
    elif customer_pin.pin == text or customer_pin.prev_pin == text:
        message = "CON Previously used PIN is not allowed, choose new PIN\n\n0. Cancel"
    else:
        customer_pin.last_pin = text
        customer_pin.save()
        message = responses.reset_pin_retype_pin()
        session.current_screen = 'reset_pin_retype_pin'
        session.save()
    return message


def reset_pin_retype_pin_screen(customer_pin, text, session):
    if customer_pin.last_pin != text or len(text) != 4 or str(text).isdigit() is False:
        message = "CON Invalid PIN\n \nChoose new PIN "
        session.current_screen = 'reset_pin_enter_new_pin'
        session.save()
    else:
        customer_pin.prev_pin = customer_pin.pin
        customer_pin.pin = text
        customer_pin.save()
        message = "END PIN reset successfully"
        close_session(session)
    return message


def block_account_request_screen(text, session, customer):
    if text == "*":
        message = responses.main_menu_second_page()
        session.current_screen = 'main_menu_second_page'
        session.save()
    else:
        try:
            acct = CustomerAccount.objects.get(customer=customer, position=text)
            acct.request_block = True
            acct.save()
            message = responses.block_account_confirm_or_cancel()
            session.current_screen = 'block_account_confirm_or_cancel'
            session.save()
        except (Exception,):
            message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
    return message


def block_account_confirm_or_cancel_screen(text, session):
    if text == "1":
        message = responses.block_account_enter_pin()
        session.current_screen = 'block_account_enter_pin'
        session.save()
    elif text == "2":
        message = responses.block_account_cancel()
        session.current_screen = 'block_account_cancel'
        session.save()
    else:
        message = responses.block_account_confirm_or_cancel()
    return message


def block_account_enter_pin_screen(text, customer_pin, customer, session):
    message = ''
    if text == customer_pin.pin:
        accounts = CustomerAccount.objects.filter(customer=customer, request_block=True)
        # CALL JAIZ API TO BLOCK ACCOUNT
        for account in accounts:
            response = block_account(account.account_no)
            if response['ResponseCode'] == "00":
                account.active = False
                account.save()
                message = responses.block_account_success()
            else:
                message = response['ResponseDescription']
        session.current_screen = 'block_account_success'
        session.save()
    else:
        message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
    return message


def detect_cat_and_select_item(text, customer, session, *, marker="NO"):
    message, success = "", True
    try:
        get_package = Package.objects.get(id=text)
        if marker == "NO":
            success = False

        elif marker == "EL":
            instance = Electricity.objects.get(customer=customer, session=session)

        elif marker == "TV":
            instance = CableSubscription.objects.get(customer=customer, session=session)

        instance.package = get_package
        instance.save()

        items_under_packages = Item.objects.filter(biller_id=get_package.biller_id).order_by("id")
        message = responses.item_list(items=items_under_packages)
        session.current_screen = f"item_list_{get_package.biller_id}_{marker}"

    except (Exception,) as err:
        log_errors(err)
        success = False

    session.save()
    return message, marker, success


def select_mno_screen(customer, text, session, request_type):
    # message = f"CON Select Network\n1. MTN\n2. Airtel\n3. 9mobile\n4. GLO"
    instance = Data.objects.filter(customer=customer, session=session).last()
    if request_type == "airtime":
        instance = Airtime.objects.filter(customer=customer, session=session).last()
    if text == '1':
        instance.network = "MTN"
    elif text == '2':
        instance.network = "Airtel"
    elif text == '3':
        instance.network = "9mobile"
    elif text == '4':
        instance.network = "GLO"
    else:
        if request_type == "airtime":
            session.current_screen = 'airtime_others_select_network'
        session.current_screen = 'data_others_select_network'
        message = responses.select_mobile_network()
        session.save()
        return message
    instance.save()
    message = responses.data_others_network_bundles(instance.network)
    session.current_screen = 'data_others_network_bundles'
    if request_type == "airtime":
        message = responses.airtime_others_confirm_pin(beneficiary=instance.beneficiary, amount=instance.amount,
                                                       network=instance.network)
        session.current_screen = 'airtime_others_confirm_pin'
    session.save()
    return message
