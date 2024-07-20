# This is the first page of the main menu
import requests

# from home.views import log_errors
from home.api import name_enquiry_local, get_bank_from_nuban, get_last_five_transactions
from home.models import BillCategory, Package, Electricity, CableSubscription
from humanize import intcomma

from django.conf import settings

charges = settings.CHARGES


def main_menu_first_page():
    message = "CON Welcome to Jaiz Bank\n\n1. Airtime - Self\n2. Airtime - Others\n3. Data\n" \
              "4. Trsf - Jaiz\n5. Trsf - Others\n6.Bills\n7. Account Bal\n" \
              "8. Next"
    return message


# This is the second page of the main menu
def main_menu_second_page():
    message = "CON 1. Last Trsf\n2. Facility Bal\n3. Donation\n4. Change PIN\n" \
              "5. Add/Remove Acct\n6. Opt Out\n7. Reset PIN\n8. Incr Limit\n" \
              "9. Block Acct\n0. Menu"
    return message


def bvn_check_success(first_name, last_name, dob):
    message = f"CON Please confirm details:\nFirst Name: {first_name}\nLast Name: {last_name}\nD-O-B: {dob}" \
              f"\n1. Open Account\n2. Cancel"
    return message


def bvn_check_fail():
    message = "END Phone number Mismatch \nPhone number not mapped to BVN"
    return message


# Account creation welcome message
def open_account_success(account_no):
    message = f"CON Welcome to Jaiz Bank. Your A/C ({account_no}) has been opened\n" \
              f"\n1. Proceed to USSD Onboarding\n2. End"
    return message


# Select Gender
def select_gender():
    message = "CON Gender\n\n1. Female \n2. Male"
    return message


# Enter account number for Jaiz Existing Users
def acct_number_input():
    message = "CON Enter your account number"
    return message


# Enter card number for Jaiz Existing Users
def card_number_input():
    message = "CON Please enter the first 6 digits and the last 4 digits of your card"
    return message


# Enter recovery code for Jaiz Existing Users
def recovery_code_input():
    message = "CON Enter your Recovery Code"
    return message


# Enter recovery code failed for Jaiz Existing Users
def failed_recovery_code_input():
    message = "CON Invalid Recovery Code \n\nEnter your last transaction amount"
    return message


# Enter last transaction for Jaiz Existing Users
def last_five_transactions(account_no):
    message = [f"CON Select Account\n"]

    for acct in account_no:
        message.append(f'{acct.position}. {acct.account_no} ')
    message.append('* Back')
    return '\n'.join(message)


def last_five_transactions_enter_pin():
    message = "CON Last 5 transactions\n \nPlease Enter your pin"
    return message


# No card number selection for Jaiz Existing Users
def no_card_number_input():
    message = "CON Please choose \n \n1. Recovery Code \n2. Last Transaction Amount"
    return message


# Input First Name
def first_name_input():
    message = "CON First Name"
    return message


# Input Last Name
def last_name_input():
    message = "CON Surname/Lastname/Family Name"
    return message


# Input Date of Birth
def date_of_birth_input():
    message = "CON Date of Birth (yyyy-mm-dd)"
    return message


# Create USSD PIN
def create_ussd_pin():
    message = "CON Please create your 4-digit USSD PIN"
    return message


# Confirm Create USSD PIN
def confirm_create_ussd_pin():
    message = "CON Confirm your USSD PIN \nEnter your 4-digit PIN again for confirmation"
    return message


# Create USSD PIN Success
def create_ussd_pin_success(account_no):
    message = f"END Thank you for choosing Jaiz Bank \nYour account number is {account_no}. We have sent " \
              f"your account number to you via SMS."
    return message


# Create USSD PIN Fail
def create_ussd_pin_fail():
    message = "CON USSD PIN Mismatch \nPlease create your 4-digit USSD PIN"
    return message


# Create USSD PIN same as Last
def ussd_pin_same_as_last():
    message = "CON You cannot use this PIN \nPlease input another 4-digit USSD PIN"
    return message


# -------------------------------------------------------------->


# Amount Self
def airtime_amount_self():
    return "CON Please enter amount"


# Respond with user's account list / Also used in Airtime Others / Used in Add or Remove Account.
def select_account(customer_account):
    l, message = [], "CON Select Account: \n"
    for account in customer_account:
        l.append(f"{account.position}. {account.account_no}")
    message += "\n".join(l)
    return message


def select_account_for_airtime_other(customer_account):
    l, message = [], "CON Select Account: \n"
    for account in customer_account:
        l.append(f"{account.position}. {account.account_no}")
    message += "\n".join(l)
    return message


# Insufficient Funds
def no_sufficient_funds():
    return "CON Insufficient account balance, \n\n0. Main Menu"


# Confirm USSD for airtime self
def confirm_ussd_for_airtime_self(msisdn, network, amount):
    return f"CON Enter your USSD PIN to top up {msisdn} on {network} with {amount} or enter 0 to cancel"


def buy_data_self_successfully(data, phone):
    return f"CON Dear {data.customer.first_name}, You have successfully loaded {data.data_amount}/{data.amount} " \
           f"{data.network} data on {phone}. Thank you for choosing Jaiz Bank.\n\n0. Main Menu "


def confirm_ussd_for_data_self():
    return "CON Enter 4 digit pin"


def confirm_ussd_for_data_others():
    return "CON Enter 4 digit PIN"


# Select Service Providers
def select_service_provider():
    return "CON Please select service provider \n1. MTN \n2. Airtel \n3. GLO"


def data_self_network_bundles(network):
    return f"CON {network} bundle:\n\n1. 150MB 1day N100 \n2. 350MB 2days N200\n3. 2.9GB 30days N1000" \
           f"\n4. 4.1GB 30days N1500\n5. 5.8GB 30days N2000"


def data_others_network_bundles(network):
    return f"CON {network} bundle:\n\n1. 150MB 1day N100 \n2. 350MB 2days N200\n3. 2.9GB 30days N1000" \
           f"\n4. 4.1GB 30days N1500\n5. 5.8GB 30days N2000"


# Airtime purchase
def airtime_self_purchase_success(airtime_instance):
    return f"CON Dear {airtime_instance.customer.first_name}, You have recharged N{airtime_instance.amount}" \
           f" on {airtime_instance.beneficiary}. Thank you for choosing Jaiz Bank.\n\n0. Main Menu"


# --------


# This will be replaced with airtime_amount_self(), because they both return the same message.
def airtime_amount_others():
    return "CON Please enter amount"


# Jaiz or Other Banks Account for Transfer
def transfer_jaiz_acct():
    return "CON Please enter beneficiary account number"


# Incorrect Account Number
def incorrect_acct_number():
    return "CON Incorrect account number, please enter correct account number to proceed"


def trnsf_others_incorrect_acct_no():
    return "CON Incorrect account number, please enter correct account number to proceed"


# Select Account for Jaiz Transfer
def jaiz_transfer_select_account(customer_account):
    count, l, message = 1, [], "CON Select Account: \n"
    for a in customer_account:
        l.append(f"{count}. {a.account_no}")
        count += 1
    message += "\n".join(l)
    return message


# Select Account for Jaiz Transfer OTHERS
def jaiz_transfer_others_select_account(customer_account):
    count, l, message = 1, [], "CON Select Account: \n"
    for a in customer_account:
        l.append(f"{count}. {a.account_no}")
        count += 1
    message += "\n".join(l)
    return message


# Message to confirm pin for transaction
def confirm_funds_transfer(fund_transfer):
    name_enquiry_response = name_enquiry_local(fund_transfer.account_no)
    if name_enquiry_response["responseCode"] != "00":
        return f"CON You are sending N{fund_transfer.amount} to {fund_transfer.account_no}. \n Charges : N{charges}" \
               f"\n Total: N{int(fund_transfer.amount) + int(charges)} \nPlease enter your PIN to complete the transfer"
    return f"CON You are sending N{fund_transfer.amount} to {name_enquiry_response['accountName']}, {fund_transfer.account_no}. \n Charges : N{charges}" \
           f"\n Total: N{int(fund_transfer.amount) + int(charges)} \nPlease enter your PIN to complete the transfer"


def confirm_funds_transfer_others(fund_transfer):
    return f"CON You are sending N{fund_transfer.amount} to {fund_transfer.receiver_name}, {fund_transfer.account_no}. \n Charges : N{charges}" \
           f"\n Total: N{int(fund_transfer.amount) + int(charges)} \nPlease enter your PIN to complete the transfer"


# Message for Successful Jaiz Transfer


def jaiz_transfer_confirmed(fund_transfer):
    message = f"CON Dear {fund_transfer.customer.first_name}, You have successfully " \
              f"transferred N{fund_transfer.amount} to {fund_transfer.receiver_name} {fund_transfer.account_no}. " \
              "Thank you for choosing Jaiz Bank\n\n0. Main Menu"
    return message


# Opt-Out Pin
def confirm_pin_to_opt_out() -> str:
    return "CON Please Enter Your PIN To Opt Out"


def opt_out_successful(customer) -> str:
    return f"END Dear {customer.first_name}, you have successfully opted out of Jaiz USSD."


def facility_balance_pin() -> str:
    return "CON Facility Balance \nPlease Enter Your PIN To Opt Out"


def facility_balance_unavailable() -> str:
    return "CON Request currently unavailable, please try again later. \n\n0. Main Menu"


# Select Account to check balance
def account_balance_select_acct(customer_account) -> str:
    l, message = [], "CON Select Account: \n"
    for account in customer_account:
        l.append(f"{account.position}. {account.account_no}")
    message += "\n".join(l)
    return message


# Pin Confirmation for Account Balance
def confirm_ussd_account_balance() -> str:
    return "CON Please enter Your PIN"


# Account Balance Response
def account_balance_msg(account_balance):
    return f"CON Your Account Balance: NGN{account_balance} \n\n0. Main Menu"


# Transfer Others Number
def others_account_number() -> str:
    return "CON Please enter beneficiary Account Number"


# Enter Bank Of Beneficiary
def enter_beneficiary_bank(account_number, session, customer, instance):
    banks_response = get_bank_from_nuban(account_number)
    # get list of banks and save to db.
    slice_range_init, slice_range_last = 0, 0
    try:
        len(banks_response['Banks'])
        if instance.next == 1:
            slice_range_init = 0
            slice_range_last = 3  # interval 3
        elif instance.next == 2:
            slice_range_init = 3
            slice_range_last = 6  # interval 3
        elif instance.next == 3:
            slice_range_init = 6  # interval 3
            slice_range_last = 9
        elif instance.next == 4:
            slice_range_init = 9  # interval 3
            slice_range_last = 12
        elif instance.next == 5:
            slice_range_init = 12  # interval 3
            slice_range_last = 15
        elif instance.next == 6:
            slice_range_init = 15  # interval 3
            slice_range_last = 18
        elif instance.next == 7:
            slice_range_init = 18  # interval 3
            slice_range_last = 21
        elif instance.next == 8:
            slice_range_init = 21  # interval 3
            slice_range_last = 24

        message, count, bank_list, bank_list_db = "CON Select bank \n", 1, [], []
        if banks_response["Banks"][slice_range_init:slice_range_last]:
            for bank in banks_response["Banks"][slice_range_init:slice_range_last]:
                bank_list_db.append(f"{count}.{bank['bankName']}.{bank['bankCode']}.{bank['liveBankCode']}")
                bank_list.append(f"{count}. {bank['bankName']}")
                count += 1

            numbered_list = "\n".join(bank_list)
            instance.bank_list_response = bank_list_db
            instance.save()
        else:
            return False
        return f"{message} {numbered_list} \n00. Next \n0. Main Menu"

    except Exception as err:
        return False


def fund_transfer_amount():
    return "CON Enter Amount"


def add_or_remove_account():
    return "CON 1. Add Account\n2. Remove Account\n\n0. Main Menu"


def select_acct_for_removal(customer_account):
    # print(customer_account.order_by("id"), "------------", customer_account)
    count, l, message = 1, [], "CON Select Account: \n"
    for a in customer_account.order_by("id"):
        l.append(f"{a.position}. {a.account_no}")
        count += 1
    message += "\n".join(l)
    return message


def warning_account_removal(account):
    return f"CON You are about to remove {account.account_no}\nEnter PIN to confirm"


def account_removal_success():
    return "CON Your account has been removed successfully \n 0. Main Menu"


def enter_acct_to_add():
    return 'CON Enter account number'


def add_wrong_number_msg():
    return "CON Please enter your valid account number\n0. Cancel"


def acct_already_exist():
    return "CON Account already exists \n0. Main Menu"


def confirm_to_add_acct(acct_no, acct_name):
    return f"CON You are about to add {acct_no} {acct_name} Enter PIN to confirm\n0. Cancel"


def successfully_added_acct():
    return "CON Your account has been added successfully \n0. Main Menu"


# -------------------------------------------------------------->


# Airtime - Others (Request for Phone Number)
def airtime_others_receiver_number():
    return "CON Enter Receiver Mobile No."


def airtime_others():
    return "CON Enter receiver mobile number"


# Airtime - Others (Enter USSD PIN)
def airtime_others_confirm_pin(beneficiary, amount, network):
    message = f"CON Enter your USSD PIN to Top Up {beneficiary} on {network} with {amount} or press 0 to cancel"
    return message


# Airtime - Others (Enter USSD PIN)
def select_mobile_network():
    message = f"CON Select Network\n1. MTN\n2. Airtel\n3. 9mobile\n4. GLO\n\n0. Main Menu"
    return message


# Airtime Amount for Self and Others
def airtime_amount():
    message = "CON Kindly enter amount"
    return message


# Transfer to other bank
def transfer_to_other_bank():
    return ""


# Amount to transfer to Jaiz account
def request_amount_to_transfer():
    return "CON Enter amount to transfer"


# Account number or name for others
def transfer_account_number():
    message = "CON Enter the ACCOUNT NUMBER or PHONE NUMBER or SURNAME of Recipient"
    return message


# Select Beneficiary from the list
def select_beneficiary(name1, name2):
    # it will be colleting details of the account from
    message = f"CON Select Beneficiary \n1. {name1} \n2. {name2}"
    return message


def buy_data_type():
    return "CON Buy Data for \n1. Self \n2. Others"


# If Beneficiary doesn't exist
def enter_beneficiary_account_number():
    message = "CON The name does not exist on Beneficiary Bank account. Enter the ACCOUNT NUMBER of Recipient"
    return message


# enter ussd pin for confirmation
def enter_ussd(amount, name, account_number, charge):
    message = f"CON Enter your USSD PIN to confirm transfer of {amount} to {name}, {account_number} @ {charge} charge. Enter 0 to cancel"
    return message


# Other Bank Transfer successfull
def other_bank_transfer_success(name, amount):
    message = f"END Transfer of {amount} to {name} is successful."
    return message


def wrong_pin():
    message = "END You entered the wrong pin."
    return message


def bill_payment_cable_tv():
    message = "CON 1. DSTV \n2. GOTV \n3. Startimes \n4. Back"
    return message


def enter_smartcard():
    message = "CON Enter your SMARTCARD Number or 0 to go back"
    return message


def incorrect_smart_num():
    message = "CON Invalid/Incorrect SMARTCARD Number. Please capture the correct number"
    return message


def select_package(provider, smart_card, name, package):
    words = [f"CON Select your Package to renew for {provider} {smart_card}, {name}"]

    for x in range(len(package)):
        add = f"{x + 1}. {package[x]}"
        words.append(add)

    add = f"{len(package) + 1}. Back"
    words.append(add)

    last = "\n".join(words)
    message = last
    return message


def select_wrong_package(provider, smart_card, name, package):
    words = [f"CON Wrong input \n \nSelect your Package to renew for {provider} {smart_card}, {name}"]

    for x in range(len(package)):
        add = f"{x + 1}. {package[x]}"
        words.append(add)

    add = f"{len(package) + 1}. Back"
    words.append(add)

    last = "\n".join(words)
    message = last
    return message


def enter_cable_tv_ussd(provider, package, smart_card, name):
    message = f"CON Enter your USSD PIN to renew {provider}, {package} for {smart_card}, {name} " \
              f"or 0 to go back or 1 to select another package"
    return message


def cable_tv_completed():
    message = "END Your transaction was processed successfully… please check your phone for TOKEN"


# Request Account Number or Phone Number or Surname of Recipient.
def account_phone_or_surname_of_recipient():
    message = "CON Enter ACCOUNT NUMBER or PHONE NUMBER or SURNAME of Recipient"
    return message


# Confirm user USSD pin
def confirm_ussd(amt_to_transfer, beneficiary_name, beneficiary_act, jaiz_charges):
    message = f"CON Enter your USSD PIN to  confirm transfer of  N{amt_to_transfer} to {beneficiary_name} " \
              f"{beneficiary_act} @ N{jaiz_charges} charge. Enter 0 to cancel"


# Success  for Transfer to Jaiz or Other banks
def transfer_success_msg(amount_transferred, recipient, beneficiary):
    # try:
    #     customer
    message = f"CON Transfer of N{amount_transferred} to {recipient} was successful. Save {beneficiary} to" \
              f" Beneficiary ? \n1.    Yes\n2.    No "
    return message, beneficiary


# Phone number is tied to multiple accounts
def multiple_acct_or_not_in_bnf_list():
    message = "CON The number is not tied to a JAIZ Bank account, Enter the ACCOUNT NUMBER or Recipient"
    return message


# Select beneficiary to transfer to
def select_beneficiary_for_transfer():
    message = "CON Select Beneficiary \n1. DOE AUSTIN \n2. DOE JOHN"
    return message


# Invalid Input
def invalid_input():
    message = "END Invalid Input"


# ENTER METER NUMBER
def enter_meter_number():
    message = "CON Enter Meter Number or  0 to go back"
    return message


# SELECT PAYMENT TYPE
def select_payment_type_page():
    message = "CON Select Payment Type\n \n1. Prepaid \n2. Postpaid"
    return message


#  ENTER AMOUNT OF ELECTRICITY
def enter_electricity_amount(electricity_obj):
    message = f"CON Please Amount to pay <<{electricity_obj.provider}>> for " \
              f"{electricity_obj.meter_number}, DOE JOHN, or 0 to go back."
    return message


# REQUEST PHINE NUMBER PAGE FOR ELECTRICITY
def electricity_enter_phone_number():
    message = "CON Please Enter Phone Number"
    return message


# CONFIRM USSD PIN, FOR ELECTRICITY PAYMENT
def electricity_confirm_ussd(electricity_obj):
    message = f"CON Enter your USSD PIN to confirm payment of {electricity_obj.amount} to" \
              f" <<{electricity_obj.provider}>>, for {electricity_obj.meter_number}, DOE JOHN " \
              f"({electricity_obj.phone_number})"


# SUCCESS AND SEND CODE TO THE ENTERED NUMBER
def success_electricity_token():
    message = "END Your transaction was processed successful...\n Please check your Phone for token"
    return message


# Create PIN menu
def create_pin_menu():
    message = "CON Create USSD PIN \n \n1. With Debit Card \n2. No Debit Card \n0. Back \n00. Main Menu"
    return message


# Change PIN menu
def change_pin_request():
    message = "CON Kindly enter your existing PIN"
    return message


def enter_new_pin_change_pin():
    message = "CON Kindly enter new PIN"
    return message


def enter_new_pin_change_pin_confirm():
    message = "CON Retype New PIN"
    return message


def change_pin_success(first_name):
    message = f"CON Dear {first_name}, your PIN successfully updated\n \n0. Main Menu"
    return message


def reset_pin_request():
    message = "CON Enter account number"
    return message


def reset_pin_enter_acct_number():
    message = "CON Select authentication method:\n \n1. Last 6 digits of debit card \n2.Token "
    return message


def reset_pin_enter_debit_card():
    message = "CON Kindly enter the last 6 digits of your debit card"
    return message


def reset_pin_enter_token():
    message = "CON Kindly enter Token"
    return message


def reset_pin_enter_new_pin():
    message = "CON Choose new PIN"
    return message


def reset_pin_retype_pin():
    message = "CON Retype your new PIN"
    return message


# PIN card number input
def pin_card_number_input():
    message = "CON Please enter the first 6 digits and the last 4 digits of your card"
    return message


# PIN account number input
def pin_acct_number_input():
    message = "CON Enter your account number"
    return message


# Current PIN input
def current_pin_input():
    message = "CON Enter your current PIN"
    return message


# Create new PIN input
def create_new_pin_input(account_no):
    message = f"CON Kindly create your 4digit PIN for A/C ({account_no})\n \nEnter 4-digit PIN "
    return message


def create_new_pin_retype():
    message = f"CON Retype your USSD PIN "
    return message


def create_new_pin_success(first_name):
    message = f"CON Dear {first_name}, thank you for signing up to Jaiz USSD\n  \n0. Main Menu"
    return message


def create_new_pin_input_invalid(account_no):
    message = f"CON Invalid PIN \nKindly create your 4digit PIN for A/C ({account_no})\n \nEnter 4-digit PIN "
    return message


# Recovery Code input for new pin
def recovery_code_new_pin_input():
    message = "CON Too many PIN change tries on your account\n \nEnter your recovery code"
    return message


def onboard_customer():
    message = "CON Welcome to Jaiz Bank \nKindly select an option to activate your USSD.\n " \
              "\n1. Active Debit Card \n2. Token"
    return message


def enter_bvn_onboard():
    message = "CON Please Enter your  BVN"
    return message


def enter_account_no_onboard():
    message = "CON Please Enter Account number"
    return message


def enter_card_no_onboard():
    message = "CON Enter the last six (6) digits of your debit card"
    return message


def enter_token_onboard():
    message = "CON Please enter Token"
    return message


def enter_new_pin_onboard(account_no):
    message = f"CON Create New Pin for A/C ({account_no})\n \nEnter 4-digit PIN "
    return message


def retype_new_pin_onboard(account_no):
    message = f"CON Kindly re-type your USSD PIN"
    return message


def enter_new_pin_onboard_invalid(account_no):
    message = f"CON PIN Mismatch \nKindly create new PIN for A/C ({account_no})\n \nEnter 4-digit PIN "
    return message


def enter_new_pin_onboard_success(first_name):
    message = f"CON Dear {first_name}, thank you for signing up to Jaiz USSD\n \n0. Main Menu"
    return message


def block_account_request(account_no):
    message, l = [f"CON Select Account \n"], []

    for acct in account_no:
        message.append(f'{acct.position}. {acct.account_no} \n')
    message.append('* Back')
    return ''.join(message)


def block_account_confirm_or_cancel():
    message = "CON Warning: If you proceed, you will not be able to perform any transaction until account " \
              "is unblocked.\n 1. Enter PIN to confirm \n2. Cancel"
    return message


def block_account_enter_pin():
    message = "CON Please enter your PIN"
    return message


def block_account_cancel():
    message = "CON 0. Main Menu"
    return message


def block_account_success():
    message = "CON You have successfully blocked your account.\n \nKindly visit any Jaiz Bank to unblock \n0. Main Menu"
    return message


def limit_agreement():
    message = "CON Do you agree to the indemity clause on www.jaizbankplc.com\n \n1. Agree \n2. Cancel"
    return message


def limit_select_account(accounts):
    message = [f"CON Select Account \n"]

    count = 1
    for account in accounts:
        account.position = count
        account.save()
        count += 1
        message.append(f'{account.position}. {account.account_no} ')
    message.append('* Back')
    return '\n'.join(message)


def limit_card_or_otp():
    message = "CON 1. Enter last 6-digit of your card \n2. OTP (token)"
    return message


def limit_enter_card_digit():
    message = "CON Kindly enter the last 6 digits of your debit card"
    return message


def limit_enter_otp():
    message = "CON Kindly enter Token"
    return message


def limit_enter_amount():
    message = "CON Enter new limit"
    return message


def limit_enter_amount_failed():
    message = "CON Limit cannot be greater than 500000, please enter limit of 500000 or less"
    return message


def limit_retype_amount():
    message = "CON Retype your limit"
    return message


def limit_enter_pin():
    message = "CON Enter your PIN"
    return message


def limit_success():
    message = "CON Your limit has been increased successfully\n \n0. Main Menu"


def opted_out_response(customer):
    return f"END Dear {customer.first_name}, you have already opted out of Jaiz USSD."


def data_others_enter_receiver_no():
    return "CON Enter Receiver's Phone Number"


def confirm_data_others_purchase(data):
    return f"CON Buy Data:\n\nReceiver: {data.beneficiary}\nBundle: {data.data_amount}/{data.amount}\nNetwork: " \
           f"{data.network}\n\n1. Proceed\n0. Main Menu"


def successful_data_other_response(data):
    return f"CON Dear {data.customer.first_name}, You have successfully loaded {data.data_amount}/N{data.amount} {data.network} data on {data.beneficiary}. " \
           "Thank you for choosing Jaiz Bank.\n\n0. Main Menu"


# Pay Bills Options
def pay_bills_option():
    biller_categories, container, message = BillCategory.objects.all().order_by("id"), list(), "CON Category: "
    for cat in biller_categories:
        container.append(f"{cat.id}. {cat.name}")
    message += "\n".join(container)
    return message


# Electricity or Utilities
def electricity_options():
    message = "CON Select your option\n \n1. EKEDC\n2. IKEJA\n3. IBADAN\n4. ABUJA\n5. KANO \n6. Back"
    return message


def category_packages(bill_category, customer, session, *, next):  # '*' makes sure that 'next' must be a kwarg
    """
    :param bill_category:
    :param customer: customer instance.
    :param session: customer's session instance.
    :param next: used to process pages to render, if 00 -> it process a new list of Packages to render.
    :return: 'CON Message' and A 'marker' used to tell what instance was created e.g  El for Electric, TV for Cable TV
    :marker: EL, TV, NO(Nothing)... Must be CAPITALIZED and Contains only 2 letters
    """
    # packages, container = Package.objects.filter(category=bill_category).order_by("id")[:8], list()
    packages, container = Package.objects.filter(category=bill_category).order_by("id")[:3], list()
    message, marker = "Select Package:", "NO"

    if Package.objects.filter(category=bill_category, name__icontains="electric"):
        # Create Electric Model Instance
        message, marker = "CON Select your Disco:", "EL"
        Electricity.objects.get_or_create(customer=customer, session=session)

    elif Package.objects.filter(category=bill_category, name__icontains="tv"):
        # Create Cable TV Model Instance
        message, marker = "CON Cable TV Billers:", "TV"
        cable_sub_instance, success = CableSubscription.objects.get_or_create(customer=customer, session=session)

        # NOTE: The following lines of code inside this 'if' statement is repetitive and will later be handled by a loop
        # Together with a request session 'current screen session parameter' e.g: screen_tv_01
        # parameters that changes during request are: 'start, stop' and always increment the .next value by 1.

        next_00 = "\n00. Next"
        packages_ = None
        if next == "00":
            # start, next_00 = 8, ""
            # while cable_sub_instance.next < ... : #  Sample loop
            if cable_sub_instance.next == 1:
                # Put these into a function
                start, stop = 3, 6
                packages_, container = Package.objects.filter(category=bill_category).order_by("id")[start:stop], list()

                next_00 = "\n00. Next" if (len(packages) >= 3 and len(
                    Package.objects.filter(category=bill_category).order_by("id")[start:]) > 3) else ""
                cable_sub_instance.next += 1
                cable_sub_instance.save()
            elif cable_sub_instance.next == 2:
                start, stop = 6, 9
                packages_, container = Package.objects.filter(category=bill_category).order_by("id")[start:stop], list()
                next_00 = "\n00. Next" if (len(packages) >= 3 and len(
                    Package.objects.filter(category=bill_category).order_by("id")[start:]) > 3) else ""
                cable_sub_instance.next += 1
                cable_sub_instance.save()

            elif cable_sub_instance.next == 3:
                start, stop = 9, 12
                packages_, container = Package.objects.filter(category=bill_category).order_by("id")[start:stop], list()
                next_00 = "\n00. Next" if (len(packages) >= 3 and len(
                    Package.objects.filter(category=bill_category).order_by("id")[start:]) > 3) else ""
                cable_sub_instance.next += 1
                cable_sub_instance.save()

            elif cable_sub_instance.next == 4:
                # Put these into a function
                start, stop = 12, 15
                packages_, container = Package.objects.filter(category=bill_category).order_by("id")[start:stop], list()

                if len(packages) >= 3 and len(packages_) > 3:
                    next_00 = "\n00. Next"
                else:
                    cable_sub_instance.next = 1
                    cable_sub_instance.save()
                    next_00 = "\n0. Menu"

                    # Works fine if needed uncomment the line of code below and also on 'views' where 'if text == '99'

                    # next_00 = "\n99. Back"
                    # session.current_screen = "category_packages_2_TV"
                    # session.save()
            elif cable_sub_instance.next == 5:
                # Put these into a function
                start, stop = 15, 18
                packages_, container = Package.objects.filter(category=bill_category).order_by("id")[start:stop], list()

                if len(packages) >= 3 and len(packages_) > 3:
                    next_00 = "\n00. Next"
                else:
                    next_00 = "\n0. Menu"

                    # Works fine, if needed uncomment the line of code below and also on 'views.py' where 'if text == '99'
                    # next_00 = "\n99. Back"
                    # session.current_screen = "category_packages_2_TV"
                    # session.save()

                cable_sub_instance.next = 1
                cable_sub_instance.save()

            try:
                for pack in packages_:
                    container.append(f"\n{pack.id}. {pack.name}")

                message += "".join(container)
                return message + next_00, marker
            except (Exception,) as err:
                # Returns the .next value to 1
                cable_sub_instance.next = 1
                cable_sub_instance.save()
                return message + "" + marker

    # The code below does not get executed during Cable Subscription flow.
    next_00 = "\n00. Next"
    if next == "00":
        # start, next_00 = 8, ""
        start, next_00 = 3, ""
        packages, container = Package.objects.filter(category=bill_category).order_by("id")[start:], list()

    for pack in packages:
        container.append(f"\n{pack.id}. {pack.name}")

    message += "".join(container)
    return message + next_00, marker


def item_list(items):
    container, message = list(), "CON Bill Items: "
    for item in items:
        container.append(f"\n{item.id}. {item.name} \u20A6{intcomma(item.amount)}")
    message += "".join(container)
    return message


def enter_customer_number_cable_tv():
    return "Enter Customer Number"


def last_5_trans_format_api_response(account_no):
    success, message = False, "CON Last Five Transactions:\n"

    try:
        # CALL JAIZ API TO GET LAST 5 TRANSACTIONS
        last_5_trans_response = get_last_five_transactions(account_no)
        remove_left_curly_brace = last_5_trans_response["responseMessage"][
                                  1:len(last_5_trans_response["responseMessage"]) - 1].replace("{", "")
        remove_right_curly_brace = remove_left_curly_brace.replace("}", "")
        final_string = remove_right_curly_brace.replace('"', "")

        split_by_comma = final_string.split(",")

        start, container, end = 0, list(), 4  # 4, 8

        for _ in range(len(split_by_comma)):
            if not split_by_comma[start:end]:
                break
            container.append(split_by_comma[start:end])
            start += 4
            end += 4

        l, count = list(), 1
        for item in container:
            amount_and_type = item[2:4]
            amount, trans_type = amount_and_type[0].split(":")[1], amount_and_type[1].split(":")[1]
            l.append(f"N{amount} {trans_type}")
            count += 1
        message += "\n".join(l) + "\n\n0. Main Menu"
        success = True
    except (Exception,) as err:
        # log_errors(err)
        message = f"CON An error has occurred, please try later\n\n0. Main Menu"

    return message, success


def enter_meter_no(*, item_name):
    return f"Enter your {item_name}"


def transaction_pin_reties(instance, session):
    from home.utils import close_session
    retry_limit = settings.PIN_TRIES
    if instance.pin_tries >= int(retry_limit):
        message = "END Maximum retries exceeded"
        instance.status = "failed"
        instance.save()
        close_session(session)
    else:
        message = "CON Incorrect PIN, kindly enter correct PIN to proceed\nEnter PIN or 0 to cancel"
    return message
