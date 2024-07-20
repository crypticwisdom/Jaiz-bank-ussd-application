# JAIZ BANK APIs
import logging
import requests
import decimal
import json
import xmltodict
from django.conf import settings

base_url = settings.API_URL
api_username = settings.API_USERNAME
api_password = settings.API_PASSWORD
api_client_ip = settings.API_CLIENT_IP
jaiz_bank_code = settings.JAIZ_BANK_CODE
json_content_type = "application/json"
xml_content_type = "application/xml"


def log_request(*args):
    for arg in args:
        logging.info(arg)


def send_sms(phone_number, message):
    # This method can be used to log SMS for sending to the specified phone number.
    url = f'{base_url}/SendSMS'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    data = dict()
    data['phoneNo'] = phone_number
    data['message'] = message

    payload = json.dumps(data)
    response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def balance_enquiry(account_no):
    # This method can be used to get account balance of an account.
    url = f'{base_url}/AccountBalance'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "accountNo": account_no
    })
    response = {"accountName": "UTHMAN OLAWALE AJAGBE",  # This is a sample response
                "phoneNo": "", "balance": "10000000.72",
                "responseCode": "00", "responseMessage": "Successful"}
    # response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def name_enquiry_local(account_no):
    # This method can be used to make Name Enquiry for account
    url = f'{base_url}/LocalNameEnquiry'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "accountNo": account_no
    })
    response = {"accountName":"UTHMAN OLAWALE AJAGBE","phoneNo":None,"responseCode":"00","responseMessage":"Successful","accountType":None,"balance":"49645732.72","branch":"2"}
    # response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def fund_transfer_others_local(session_id, sender_acct, receiver_acct, amount, narration, charges,
                               channel_code, sender_phone, sender_balance):
    # This transaction type enables a sender to move funds from his/her own account to another account in another Bank
    url = f'{base_url}/LocalFTUSSD'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    amount_to_send = decimal.Decimal(amount)
    amount_to_charge = decimal.Decimal(charges)
    amount_total = amount_to_send + amount_to_charge
    sending_bal = decimal.Decimal(sender_balance)

    payload = json.dumps({
        "CreditAccount": receiver_acct,
        "DebitAccount": sender_acct,
        "Amount": str(amount_to_send),
        "Fee": str(amount_to_charge),
        "Narration": narration,
        "SessionID": session_id,
        "ChannelCode": channel_code,
        "phoneNo": sender_phone,
        # "pin": "8585",
        "data": {
            "accountNumber": sender_acct,
            "transactionKey": session_id,
            "transactionType": "USSD",
            "transactionAmount": str(amount_to_send),
            "transactionDesc": narration,
            "beneficiaryBank": "",
            "accountBranch": "38",
            "transactionLocation": "",
            "clientIp": api_client_ip,
            "deviceNumber": "",
            "activationDate": "",
            "phoneNumber": sender_phone,
            "beneficiaryAccount": receiver_acct,
            "balanceEnquiry": "N",
            "transactionAmountLocal": str(amount_total),
            "debitCreditIndicator": "D",
            "accountAvailableBalance": str(sending_bal),
            "p1": "",
            "p2": "",
            "p3": "",
            "p4": "",
            "p5": "",
            "p6": "",
            "p7": "",
            "p8": "",
            "p9": "",
            "p10": "",
            "LoginName": None
        }
    })
    response = {"responseCode": "00", "responseMessage": "Successful", "responseDescription": "Successful"}
    # response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def nip_log_reversal(session_id):
    # Log reversal for unsuccessful transactions
    # To be called if TSQ returns failed or response code "25" after 5minutes
    url = f'{base_url}/LogReversal'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "sessionID": session_id
    })
    response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def interbank_name_enquiry(session_id, bank_code, account_no, channel_code):
    # Useful to detect situations where the originating customer specifies a wrong beneficiary account.
    # Name Enquiry Transaction type affords the bank the opportunity of comparing intended beneficiary name with the
    # account name tied to the provided beneficiary account in the destination bank, before confirming a transfer
    url = f'{base_url}/InterBankNameEnquiry'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = xml_content_type
    header['Accept'] = xml_content_type

    payload = f"<NESingleRequest>" \
              f"<SessionID>{session_id}</SessionID>" \
              f"<DestinationInstitutionCode>{bank_code}</DestinationInstitutionCode>" \
              f"<ChannelCode>{channel_code}</ChannelCode>" \
              f"<AccountNumber>{account_no}</AccountNumber>" \
              f"</NESingleRequest>"
    # response = requests.request('POST', url, data=payload, headers=header).text
    # log_request(url, header, payload, response)
    # parsed = xmltodict.parse(response)
    # response = json.dumps(parsed)

    response = {"NESingleResponse": {
        "SessionID": "000006181225000017000000000001",
        "DestinationInstitutionCode": "000004",
        "ChannelCode": "7",
        "AccountNumber": "2064702339",
        "AccountName": "MAJALISA PETER",
        "BankVerificationNumber": "22186708345",
        "KYCLevel": "",
        "ResponseCode": "00"
        }
    }
    return response


def nip_fund_transfer(session_id, name_enq_ref, bank_code, narration, amount, **kwargs):
    # This transaction type enables a sender to move funds from his/her own account to another account in another Bank
    url = f'{base_url}/NIPFundsTransfer'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = xml_content_type
    header['Accept'] = xml_content_type

    amount_to_send = decimal.Decimal(amount)

    payload = f"<FTSingleCreditRequest>" \
              f"<SessionID>{session_id}</SessionID>" \
              f"<NameEnquiryRef>{name_enq_ref}</NameEnquiryRef>" \
              f"<DestinationInstitutionCode>{bank_code}</DestinationInstitutionCode>" \
              f"<ChannelCode>{kwargs.get('channel_code')}</ChannelCode>" \
              f"<BeneficiaryAccountName>{kwargs.get('beneficiary_acct_name')}</BeneficiaryAccountName>" \
              f"<BeneficiaryAccountNumber>{kwargs.get('beneficiary_acct_no')}</BeneficiaryAccountNumber>" \
              f"<BeneficiaryBankVerificationNumber>{kwargs.get('beneficiary_bvn_no')}</BeneficiaryBankVerificationNumber>" \
              f"<BeneficiaryKYCLevel>{kwargs.get('beneficiary_kyc')}</BeneficiaryKYCLevel>" \
              f"<OriginatorAccountName>{kwargs.get('sender_acct_name')}</OriginatorAccountName>" \
              f"<OriginatorAccountNumber>{kwargs.get('sender_acct_no')}</OriginatorAccountNumber>" \
              f"<OriginatorBankVerificationNumber>{kwargs.get('sender_bvn_no')}</OriginatorBankVerificationNumber>" \
              f"<OriginatorKYCLevel>{kwargs.get('sender_kyc')}</OriginatorKYCLevel>" \
              f"<TransactionLocation></TransactionLocation>" \
              f"<Narration>{narration}</Narration>" \
              f"<PaymentReference>{kwargs.get('payment_ref')}</PaymentReference>" \
              f"<Amount>{amount_to_send}</Amount>" \
              f"</FTSingleCreditRequest>"
    # response = requests.request('POST', url, headers=header, data=payload).text
    # log_request(url, header, payload, response)
    # parsed = xmltodict.parse(response)
    # response = json.dumps(parsed)

    response = {"FTSingleResponse": {
        "SessionID": "000006181225000017000000000001",
        "ResponseCode": "00"
        }
    }
    return response


def nip_transaction_status(session_id, channel_code):
    # call this airtime, data, other bank transfer
    # This a transaction status query that enables the bank to query the status of a transaction sent earlier.
    url = f'{base_url}/TSQ'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = xml_content_type
    header['Accept'] = xml_content_type

    payload = f"<TSQuerySingleRequest>" \
              f"<SourceInstitutionCode>{jaiz_bank_code}</SourceInstitutionCode>" \
              f"<ChannelCode>{channel_code}</ChannelCode>" \
              f"<SessionID>{session_id}</SessionID>" \
              f"</TSQuerySingleRequest>"
    response = requests.request('POST', url, headers=header, data=payload).text
    log_request(url, header, payload, response)
    parsed = xmltodict.parse(response)
    response = json.dumps(parsed)
    sample_response = {"TSQuerySingleResponse": {
        "SourceInstitutionCode": "000006",
        "ChannelCode": "7",
        "SessionID": "000006181225000017000000000001",
        "ResponseCode": "00"
        }
    }
    return response


def get_bank_from_nuban(account_no):
    # This method can be used to get details of all financial institutions according to NIBSS.
    # It returns list of possible banks associated with account number
    url = f'{base_url}/GetBankFromNUBAN'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "nuban": account_no
    })
    # response = requests.request('POST', url, headers=header, data=payload).json()
    response = {"Banks":[{"bankName":"Access","bankCode":"044","liveBankCode":"000014"},{"bankName":"FirstBank","bankCode":"011","liveBankCode":"000016"},{"bankName":"UBA","bankCode":"033","liveBankCode":"000004"}]}
    log_request(url, header, payload, response)
    return response


def bill_payment_cable_tv(email, phone_no, payment_code, amount, customer_id, payment_type):
    # This method will be called to make payments for bills and mobile recharge (Quickteller related transactions)

    # Note: Payment Type can either be Bills or VTUP
    # For Bills payment and Mobile Recharges, call the LocalFT method to debit the customer first, passing ‘3’ as the
    # Channel Code. Upon Successful debit, you can then call the bills payment method to make bills payment

    url = f'{base_url}/BillsPaymentAdvice'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    data = dict()
    data['Email'] = email
    data['Phone'] = phone_no
    data['PaymentCode'] = payment_code
    data['Amount'] = amount
    data['CustomerID'] = customer_id
    data['PaymentType'] = payment_type

    payload = json.dumps(data)
    response = {"responseCode": "00", "responseMessage": "Successful"}
    # response = requests.request('POST', url, headers=header, data=payload).json()
    log_request(url, header, payload, response)
    return response


def get_biller_category():
    # This method returns the different categories of billers
    url = f'{base_url}/GetBillerCategory'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = {}
    # response = requests.request('POST', url, headers=header, data=payload).json()
    response = [{"ID":1,"QuickTellerCategoryId":1,"Name":"Utilities","Description":"Pay Utility Bills here","Visible":True,"PictureUrl":None},{"ID":2,"QuickTellerCategoryId":2,"Name":"Cable TV","Description":"Pay your cable TV bill here","Visible":True,"PictureUrl":None},{"ID":5,"QuickTellerCategoryId":5,"Name":"Internet Services","Description":"Pay for your other subscriptions ","Visible":True,"PictureUrl":None},{"ID":6,"QuickTellerCategoryId":6,"Name":"Government Payments","Description":"State and Ministry Payments","Visible":True,"PictureUrl":None},{"ID":11,"QuickTellerCategoryId":11,"Name":"Travel and Hotel","Description":"Airline tickets and hotel reservation payments","Visible":True,"PictureUrl":None},{"ID":12,"QuickTellerCategoryId":12,"Name":"Transport and Toll Payments","Description":"Toll payments","Visible":True,"PictureUrl":None},{"ID":33,"QuickTellerCategoryId":33,"Name":"School and Exam Fees","Description":"Schools","Visible":True,"PictureUrl":None}]
    log_request(url, header, payload, response)
    return response


def get_biller_category_by_id(category_id):
    # This method returns list of billers
    url = f'{base_url}/GetBillerCategoryByID'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "CategoryID": category_id
    })
    # response = requests.request('POST', url, headers=header, data=payload).json()
    response = {"BillItems":[{"billerID":496,"Name":"Cable Africa  Network TV(CanTV)","Surcharge":"10000","ShortName":"Cable Africa  Network TV(CanTV)"},{"billerID":113,"Name":"DAARSAT Communications","Surcharge":"10000","ShortName":"DAARSAT Communications"},{"billerID":536,"Name":"DSTV Box Office Wallet Topup","Surcharge":"10000","ShortName":"DSTV Box Office Wallet Topup"},{"billerID":104,"Name":"DSTV Subscription","Surcharge":"10000","ShortName":"DSTV Subscription"},{"billerID":459,"Name":"GoTV","Surcharge":"10000","ShortName":"GoTV"},{"billerID":308,"Name":"Infinity TV Payments","Surcharge":"10000","ShortName":"Infinity TV Payments"},{"billerID":977,"Name":"iROKOtv","Surcharge":"10000","ShortName":"iROKOtv"},{"billerID":3126,"Name":"Kwese TV","Surcharge":"10000","ShortName":"Kwese TV"},{"billerID":3431,"Name":"Linda Ikeji TV","Surcharge":"10000","ShortName":"Linda Ikeji TV"},{"billerID":720,"Name":"Montage Cable TV","Surcharge":"10000","ShortName":"Montage Cable TV"},{"billerID":112,"Name":"MyTV Smart Payment","Surcharge":"10000","ShortName":"MyTV Smart Payment"},{"billerID":341,"Name":"Play Subscription","Surcharge":"10000","ShortName":"Play Subscription"},{"billerID":240,"Name":"Startimes Payments","Surcharge":"10000","ShortName":"Startimes Payments"},{"billerID":3145,"Name":"TSTV","Surcharge":"10000","ShortName":"TSTV"}],"responseCode":"00","responseDescription":"Successful"}
    log_request(url, header, payload, response)
    return response


def get_items_by_biller_id(biller_id):
    # This method returns the list of billable items for a particular category
    url = f'{base_url}/GetPaymentItems'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "billerid": biller_id
    })
    # response = requests.request('POST', url, headers=header, data=payload).json()
    # log_request(url, header, payload, response)
    response = {"Items": [
        {"ID": 64,
         "ProviderRecognizedItemId": 28,
         "Name": "Access",
         "Description": "",
         "ConsumerIdField": "DSTV Smart Card Number",
         "Code": "28",
         "Amount": "200000",
         "ConvertedAmount": 200000,
         "BillID": 104,
         "IsAmountFixed": False,
         "SortOrder": 0,
         "PictureId": 0,
         "PaymentCode": "10428",
         "MiniAmount": None,
         "MaxAmount": None,
         "IsVisible": True},{"ID": 65,"ProviderRecognizedItemId": 32,"Name": "Access + Asia","Description": "","ConsumerIdField": "DSTV Smart Card Number", "Code": "32","Amount": "740000","ConvertedAmount": 740000,"BillID": 104,"IsAmountFixed": False,"SortOrder": 0,"PictureId": 0,"PaymentCode": "10432", "MiniAmount": None, "MaxAmount": None, "IsVisible": True}]}
    return response


def local_transaction_status(session_id):
    # This will be used to confirm status of local transactions
    url = f'{base_url}/LocalTSQ'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "SessionID": session_id
    })
    response = requests.request('POST', url, headers=header, data=payload).json()
    log_request(url, header, payload, response)
    return response


def get_customer_acct_by_phone_no(phone_no):
    # This method returns all accounts associated with the specified phone number
    url = f'{base_url}/GetAccountsByPhoneNo'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "phoneNo": phone_no
    })
    response = requests.request('POST', url, headers=header, data=payload).json()
    log_request(url, header, payload, response)
    return response


def bvn_validation(bvn_no):
    # This method returns all accounts associated with the specified phone number
    url = f'{base_url}/BVNValidation'
    header = dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    payload = json.dumps({
        "bvn": bvn_no
    })
    response = requests.request('POST', url, headers=header, data=payload).text
    log_request(url, header, payload, response)
    parse = xmltodict.parse(response)
    response = json.dumps(parse)
    sample_response = {"SearchResult": {
        "BvnSearchResult": {
            "Bvn": "22162611742",
            "RegistrationDate": "13-DEC-14",
            "FirstName": "UTHMAN",
            "MiddleName": "OLAWALE",
            "LastName": "AJAGBE",
            "DateOfBirth": "29-May-85",
            "PhoneNumber": "08054198154",
            "EnrollmentBranch": "GARKI, AREA 3 - ABUJA",
            "EnrollmentBank": "058"
            },
        "ResultStatus": "00"
        }
    }
    return response


def open_acct_with_bvn(phone_number, bvn):
    url = f'{base_url}/OpenAccountBVN'

    data, header = dict(), dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    data['bvn'] = bvn
    data['phoneNo'] = phone_number

    payload = json.dumps(data)
    response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def block_account(account_no):
    url = f'{base_url}/BlockAccount'

    data, header = dict(), dict()
    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    data['Account'] = account_no
    data['Reason'] = 106

    payload = json.dumps(data)
    response = requests.request('POST', url, data=payload, headers=header).json()
    log_request(url, header, payload, response)
    return response


def get_last_five_transactions(account_no):
    url = f"{base_url}/lastFiveTrans"
    header, data = {}, {}

    header['username'] = api_username
    header['password'] = api_password
    header['Content-Type'] = json_content_type

    data['accountNo'] = account_no

    payload = json.dumps(data)

    # response = requests.request('POST', url, data=payload, headers=header).json()
    # log_request(url, header, payload, response)
    response = {
        "responseCode": "00",
        "responseMessage": "[{\"TransDate\":\"2022-02-07T00:00:00\",\"Narration\":\"\",\"Amount\":300.0,\"TransType\":\"CR\"},"
                           "{\"TransDate\":\"2022-02-07T00:00:00\",\"Narration\":\"\",\"Amount\":1500.0,\"TransType\":\"DR\"},"
                           "{\"TransDate\":\"2022-02-07T00:00:00\",\"Narration\":\"\",\"Amount\":3000.0,\"TransType\":\"CR\"},"
                           "{\"TransDate\":\"2022-02-07T00:00:00\",\"Narration\":\"\",\"Amount\":600.0,\"TransType\":\"DR\"},"
                           "{\"TransDate\":\"2022-02-07T00:00:00\",\"Narration\":\"\",\"Amount\":500.0,\"TransType\":\"DR\"}]",
        "responseDescription": None
    }
    return response

