import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings

from . import utils
from .responses import transaction_pin_reties

from .utils import *
from . import screens
from .api import *

retry_limit = settings.PIN_TRIES


class UpdateBillCategory(APIView):
    permission_classes = []

    def get(self, request):
        utils.update_bill_categories()
        return Response({"message": "Bill category has been updated."})


class UpdatePackage(APIView):
    permission_classes = []

    def get(self, request):
        utils.update_packages()
        return Response({"message": "Package model has been updated."})


class UpdateItem(APIView):
    permission_classes = []

    def get(self, request):
        utils.update_items()
        return Response({"message": "Item model has been Updated"})


class EndPoints(APIView):
    permission_classes = []

    def get(self, request):
        utils.update_items()
        utils.update_packages()
        utils.update_bill_categories()
        return Response({"message": "Success"})


class HomeView(APIView):
    permission_classes = []

    def get(self, request):
        msisdn = request.GET.get('msisdn')
        session_id = request.GET.get('sessionid')
        network = request.GET.get('network')
        text = request.GET.get('input')
        port = request.GET.get('sendussd_port')

        jaiz_bank_code = settings.JAIZ_BANK_CODE
        current_time = time.strftime('%Y%m%d%H%M%S')

        if not session_id:
            session_id = f"{jaiz_bank_code}{current_time}" + str(uuid.uuid4().int)[:5]

        ###############################################
        # Checks params sent and if session has ended #
        ###############################################
        try:
            success, session, detail = perform_checks(request, session_id)
            if success is False:
                message = f"END {detail}"
                send_response(port, msisdn, text, session_id, message)
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            message = f"END {str(ex)}"
            send_response(port, msisdn, text, session_id, message)
            log_errors(ex)
            return Response({'message': f"END {str(ex)}"}, status=status.HTTP_400_BAD_REQUEST)

        ####################################
        # Customer API and Database Checks #
        ####################################
        """
            Description: This block of code checks the DB if the user's phone no. is present in our Customer DB.
            If customer instance is not found then, it calls the Jaiz Api with the user's phone no. to see if there
            are account associated with it. If True then, it creates a customer instance and also creates customer 
            accounts instance for the number of Jaiz bank accounts returned. Else: it ends the session.
        """
        # try:
        customer, success = Customer.objects.get_or_create(msisdn=msisdn)
        if not customer.onboarded and text == "":
            # Get account(s) with phone number from Jaiz API
            # get_account_response = get_customer_acct_by_phone_no(msisdn)

            get_account_response = {"AccountNumbers": ["0000578280", "0000626325"], "ResponseCode": "00",
                                    "ResponseDescription": "Successful"}
            count = 1
            if get_account_response["ResponseCode"] == "00":
                # Create Customer and Customer Account
                for account in get_account_response["AccountNumbers"]:
                    CustomerAccount.objects.get_or_create(customer=customer, account_no=account, position=count)
                    count += 1

                message = responses.onboard_customer()
                session.current_screen = 'onboard_customer'
            else:
                message = responses.open_account_with_bank()
                session.current_screen = 'open_account_with_bank'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # ------------------------ END -------------------------------->

        customer_account = None
        if CustomerAccount.objects.filter(customer=customer).exists():
            customer_account = CustomerAccount.objects.filter(customer=customer).last()

        # check if user has opted-out already
        if customer.active is False:
            message = responses.opted_out_response(customer)
            session.current_screen = 'opted_out_response'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            close_session(session)
            return Response({'message': message})

        # CREATE ONE_TIME BENEFICIARY DIGITS
        ot_beneficiary, created = SessionBeneficiary.objects.get_or_create(session=session)

        # CREATE CUSTOMER_PIN TABLE
        customer_pin, created = CustomerPin.objects.get_or_create(customer=customer)

        # BENEFICIARY FOR TRANSFER, BILL PAYMENT, AND AIRTIME PURCHASE
        if str(text).isnumeric() and len(text) >= 6:
            ot_beneficiary.beneficiary = text
            ot_beneficiary.save()

        if str(text).isnumeric() and len(text) == 4:
            ot_beneficiary.beneficiary = text
            ot_beneficiary.save()

        # SET CURRENT SCREEN FROM SESSION_ID
        current_screen = session.current_screen

        message = 'END Invalid Input'

        if (text == "" or text == "0") and customer.onboarded is False:
            message = responses.onboard_customer()
            session.current_screen = 'onboard_customer'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        if current_screen == 'onboard_customer' and customer.onboarded is False:
            message = screens.onboard_customer_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        if (text == "0" or text == "") and customer.onboarded is True and customer.active is True:
            message = responses.main_menu_first_page()
            session.current_screen = 'main_menu_first_page'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif session.current_screen == "no_sufficient_funds" and text != "0":
            message = responses.no_sufficient_funds()
            session.current_screen = 'no_sufficient_funds'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<---------------- ACCOUNT OPENING AND ON-BOARDING SECTION BEGINS --------------->>>>>>>>>>>>>>

        elif customer.bvn and customer.onboarded is False and text == '' and current_screen == 'open_account_success':
            message = responses.onboard_customer()
            session.current_screen = 'onboard_customer'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'open_account_with_bank':
            message = screens.open_account_with_bank_screen(customer, text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'bvn_check_success':
            message = screens.bvn_check_success_screen(customer, text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'open_account_success':
            message = screens.open_account_success_screen(customer, text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'create_new_pin_input':
            message = screens.create_new_pin_input_screen(customer, text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'create_new_pin_retype':
            message = screens.create_new_pin_retype_screen(customer, text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<------------------ ACCOUNT OPENING AND ON-BOARDING SECTION ENDS ---------------------->>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<------------------- NEW CUSTOMER ON-BOARDING BEGINS ---------------------->>>>>>>>>>>>>>>>>>>

        elif current_screen == 'onboard_customer':
            message = screens.onboard_customer_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'enter_card_no_onboard' or current_screen == 'enter_token_onboard':
            message = screens.card_token_onboarding_screen(session, text, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'enter_account_no_onboard':
            if len(text) == 10 and CustomerAccount.objects.filter(account_no=text, customer=customer).exists():
                message = responses.enter_new_pin_onboard(text)
                session.current_screen = 'enter_new_pin_onboard'
            else:
                # Invalid account number input
                message = responses.enter_account_no_onboard()
                session.current_screen = 'enter_account_no_onboard'
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'enter_new_pin_onboard':
            account_no = customer_account.account_no
            message = screens.enter_new_pin_onboard_screen(account_no, text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'retype_new_pin_onboard':
            account_no = customer_account.account_no
            message = screens.retype_new_pin_onboard_screen(text, customer_pin, session, customer, account_no)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<<<<<<<<------------------- NEW CUSTOMER ON-BOARDING ENDS ---------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<<<<<<------------------------ MAIN MENU DISPLAY ------------------------->>>>>>>>>>>>>>>>>>>>

        # MAIN MENU OPTIONS
        # These are MENUS under the main screen display
        elif current_screen == "main_menu_first_page":
            # Create Airtime Instance for this.
            message = screens.main_menu_first_page_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<<<<<<<<------------------- SECOND SCREEN MENU BEGINS ---------------------->>>>>>>>>>>>>>>>>>>
        elif current_screen == "main_menu_second_page":
            message = screens.main_menu_second_page_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})
        # <<<<<<<<<<<<<<<<------------------- SECOND SCREEN MENU END ---------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<------------------ LAST FIVE TRANSACTION MENU BEGINS --------------------->>>>>>>>>>>>>>>>>>>
        elif current_screen == 'last_five_transactions':
            message = screens.last_five_transactions_screen(text, customer, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'last_five_transactions_enter_pin':
            try:
                acct = CustomerAccount.objects.filter(customer=customer, request_transaction=True).last()
                if decrypt_text(customer_pin.pin) == text:
                    account_no = acct.account_no

                    message, success = responses.last_5_trans_format_api_response(account_no)
                    session.current_screen = "last_5_trans_format_api_response"
                    acct.request_transaction = False
                    acct.save()
                else:
                    message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"

            except Exception as err:
                acct = CustomerAccount.objects.get(customer=customer, request_transaction=True)
                acct.request_transaction = False
                acct.save()
                message = "CON An error has occurred, please try later\n\n0. Main Menu"
                log_errors(err)

            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})
        # <<<<<<<<<<<<<<<<------------------ LAST FIVE TRANSACTION MENU END --------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<---------------------- Buy Data Self ------------------------------------------>>>>>>>>>>>>>>
        elif session.current_screen == "buy_data_type":
            data = Data.objects.create(customer=customer, session=session)
            if text.isnumeric() and text == "1":
                # Data Purchase Type is self by default, so there's no for update the data purchase_type field to self.
                data.network = network
                message = responses.data_self_network_bundles(network)
                session.current_screen = "data_self_network_bundles"

            elif text.isnumeric() and text == "2":
                data.purchase_type = "others"
                message = responses.data_others_enter_receiver_no()
                session.current_screen = "data_others_enter_receiver_no"

            else:
                message = screens.main_menu_first_page_screen(text, session, customer)
                session.current_screen = "main_menu_first_page_screen"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            data.save()
            return Response({"message": message})
        #
        elif session.current_screen == "data_self_network_bundles":
            if text.isnumeric():
                # Check the user's bundle selection
                # Update Data instance with amount and the amount of data
                data = Data.objects.filter(customer=customer, session=session, purchase_type="self", status="pending").last()

                # The below should be removed when API to fetch data plans is available
                if text == "1":
                    data.amount = 100
                    data.data_amount = "150MB"
                elif text == "2":
                    data.amount = 200
                    data.data_amount = "350MB"
                elif text == "3":
                    data.amount = 1000
                    data.data_amount = "2.9GB"
                elif text == "4":
                    data.amount = 1500
                    data.data_amount = "4.1GB"
                elif text == "5":
                    data.amount = 2000
                    data.data_amount = "5.8GB"
                else:
                    message = responses.data_self_network_bundles(network)
                    session.current_screen = "data_self_network_bundles"
                    session.save()
                    send_response(port, msisdn, text, session_id, message)
                    return Response({"message": message})

                # Respond with account selection
                data.save()
                customer_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
                message = responses.select_account(customer_accounts)
                session.current_screen = "select_account_data_self"
            else:
                message = responses.data_self_network_bundles(network)
                session.current_screen = "data_self_network_bundles"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})
        #
        elif session.current_screen == "select_account_data_self":
            try:
                customer_account = CustomerAccount.objects.get(customer=customer, position=text)
                data = Data.objects.filter(customer=customer, session=session, status="pending",
                                           purchase_type="self").last()
                data.customer_account = customer_account
                data.save()
                # Check Account Balance
                balance = 0
                balance_check = balance_enquiry(customer_account)
                if balance_check["responseCode"] == "00":
                    balance = decimal.Decimal(balance_check["balance"])

                if balance > decimal.Decimal(data.amount) and data.amount > 1:
                    description = f"Ref. {session_id} Top-up IFO {balance_check['accountName']} " \
                                  f"{msisdn} {data.customer_account.account_no}"
                    fund_transfer_response = fund_transfer_others_local(
                        session_id=session_id, sender_acct=data.customer_account.account_no, receiver_acct=0000000000,
                        amount=data.amount, narration=description, charges=decimal.Decimal(0.0),
                        channel_code=settings.AIRTIME_AND_DATA_CHANNEL_CODE, sender_phone=msisdn,
                        sender_balance=balance_check["balance"]
                    )

                    # If Fund Transfer is successful then, call API to top user
                    if fund_transfer_response['responseCode'] == "00":
                        # call top-up api to top up customer
                        bill_payment_response = bill_payment_cable_tv(
                            email="", phone_no=msisdn, payment_code="10401", amount=data.amount, customer_id=msisdn,
                            payment_type="VTUP"
                        )

                        if bill_payment_response["responseCode"] == "00":
                            message = responses.buy_data_self_successfully(data, msisdn)
                            session.current_screen = "airtime_self_purchase_success"
                            session.save()
                            data.status = "success"
                            data.save()
                        else:
                            message = "CON Error processing request, please try again later.\n\n0. Main Menu"
                            data.status = "failed"
                            data.save()
                            FundReversal.objects.create(
                                customer=customer, msisdn=msisdn, customer_account=data.customer_account,
                                amount=data.amount,
                                session_id=session, transaction_type="Data Self"
                            )

                    elif fund_transfer_response['responseCode'] == '25':
                        # response_nip_transaction_status = nip_transaction_status(session_id=session_id, channel_code=7)
                        # call nip_transaction_status-tsq after 5mins How the 5 minutes timing would work: Create a model that
                        # keeps the records going into the tsq including session_id the model would have fields: time to
                        # run, status, ran?-> True or False

                        FundReversal.objects.create(
                            customer=customer, msisdn=msisdn, customer_account=data.customer_account,
                            amount=data.amount,
                            session_id=session, transaction_type="Data Self"
                        )
                    else:
                        message = "CON Error processing request, please try again later.\n\n0. Main Menu"
                        data.status = "failed"
                        data.save()
                        FundReversal.objects.create(
                            customer=customer, msisdn=msisdn, customer_account=data.customer_account,
                            amount=data.amount,
                            session_id=session, transaction_type="Data Self"
                        )

                else:
                    message = responses.no_sufficient_funds()
                    session.current_screen = "no_sufficient_funds"
                    data.status = "failed"
                    data.save()
            except (Exception,) as err:
                customer_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
                message = responses.select_account(customer_accounts)
                session.current_screen = "select_account_data_self"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        # <<<<<<<<<<<<<<---------------------- Buy Data Self Ends ------------------------------------->>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<---------------------- Buy Data Others ------------------------------------------>>>>>>>>>>>>>>
        elif session.current_screen == "data_others_enter_receiver_no":
            if text.isnumeric() and len(text) == 11:
                data = Data.objects.filter(customer=customer, session=session, purchase_type="others", status="pending").last()
                data.beneficiary = text
                look_up = False
                if look_up is False:
                    data.save()
                    message = responses.select_mobile_network()
                    session.current_screen = 'data_others_select_network'
                    send_response(port, msisdn, text, session_id, message)
                    session.save()
                    return Response({"message": message})
                mno = "MTN"  # MNO from LOOKUP
                data.network = mno
                data.save()
            else:
                message = responses.data_others_enter_receiver_no()
                session.current_screen = "data_others_enter_receiver_no"
            session.current_screen = "data_others_select_network"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen == "data_others_select_network":
            message = screens.select_mno_screen(customer, text, session, "data")
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen == "data_others_network_bundles":
            data = Data.objects.filter(customer=customer, session=session, purchase_type="others", status="pending").last()
            if text.isnumeric():
                # Check the user's bundle selection
                # Update Data instance with amount and the amount of data
                # The below should be removed when API to fetch data plans is available
                if text == "1":
                    data.amount = 100
                    data.data_amount = "150MB"
                elif text == "2":
                    data.amount = 200
                    data.data_amount = "350MB"
                elif text == "3":
                    data.amount = 1000
                    data.data_amount = "2.9GB"
                elif text == "4":
                    data.amount = 1500
                    data.data_amount = "4.1GB"
                elif text == "5":
                    data.amount = 2000
                    data.data_amount = "5.8GB"
                else:
                    message = responses.data_others_network_bundles(data.network)
                    session.current_screen = "data_others_network_bundles"
                    session.save()
                    send_response(port, msisdn, text, session_id, message)
                    return Response({"message": message})

                # Respond with account selection
                data.save()
                message = responses.confirm_data_others_purchase(data)
                session.current_screen = "confirm_data_others_purchase"

            else:
                message = responses.data_others_network_bundles(data.network)
                session.current_screen = "data_others_network_bundles"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen == "confirm_data_others_purchase":
            # user enters 1 to confirm and 0 to cancel
            customer_account = CustomerAccount.objects.filter(customer=customer).order_by("id")
            if text.isnumeric() and text == "1":
                # take customer to select account page
                # save the confirmation to data instance
                message = responses.select_account(customer_account)
                session.current_screen = "data_others_select_account"
            else:
                data = Data.objects.filter(customer=customer, session=session, purchase_type="others",
                                           status="pending").last()
                message = responses.confirm_data_others_purchase(data)
                session.current_screen = "confirm_data_others_purchase"
            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})
        #
        elif session.current_screen == "data_others_select_account":
            try:
                customer_account = CustomerAccount.objects.filter(customer=customer).order_by("id")
                data = Data.objects.filter(customer=customer, session=session, purchase_type="others",
                                           status="pending").last()
                selected_account = CustomerAccount.objects.get(customer=customer, position=text)
                data.customer_account = selected_account
                data.save()

                # check if customer can purchase this data plan (account balance check)
                account_balance_response = balance_enquiry(selected_account.account_no)
                acct_balance_check = (account_balance_response["responseCode"]) and \
                                     decimal.Decimal(account_balance_response["balance"]) > decimal.Decimal(data.amount)
        #
                if acct_balance_check:
                    message = responses.confirm_ussd_for_data_others()
                    session.current_screen = "confirm_ussd_for_data_others"
                else:
                    message = responses.no_sufficient_funds()
                    session.current_screen = "no_sufficient_funds"

            except (Exception,) as err:
                message = responses.select_account(customer_account)
                session.current_screen = "data_others_select_account"
                log_errors(err)

            session.save()
            send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})
        #
        elif session.current_screen == "confirm_ussd_for_data_others":
            data = Data.objects.filter(customer=customer, session=session, purchase_type="others",
                                       status="pending").last()
            if decrypt_text(customer_pin.pin) == text:
                # Debit customer and top up beneficiary data balance
                # Do a FundReversal
                # update status of data instance

                balance_check = balance_enquiry(data.customer_account.account_no)
                description = f"Ref. {session_id} Top-up IFO {balance_check['accountName']} " \
                              f"{msisdn} {data.customer_account.account_no}"

                fund_transfer_response = fund_transfer_others_local(
                    session_id=session_id, sender_acct=data.customer_account.account_no, receiver_acct=0000000000,
                    amount=data.amount, narration=description, charges=decimal.Decimal(0.0),
                    channel_code=settings.AIRTIME_AND_DATA_CHANNEL_CODE, sender_phone=msisdn,
                    sender_balance=balance_check["balance"]
                )

                if fund_transfer_response['responseCode'] == "00":
                    # call top-up api to top up customer
                    bill_payment_response = bill_payment_cable_tv(email="", phone_no=data.beneficiary, payment_code="10401",
                                                                  amount=data.amount,
                                                                  customer_id=msisdn,
                                                                  payment_type="VTUP")
                    if bill_payment_response["responseCode"] == "00":
                        message = responses.successful_data_other_response(data)
                        session.current_screen = "successful_data_other_response"
                        session.save()
                        data.status = "success"
                        data.save()

                elif fund_transfer_response['responseCode'] == '25':
                    # response_nip_transaction_status = nip_transaction_status(session_id=session_id, channel_code=7)
                    # call nip_transaction_status-tsq after 5mins How the 5 minutes timing would work: Create a model that
                    # keeps the records going into the tsq including session_id the model would have fields: time to
                    # run, status, ran?-> True or False

                    FundReversal.objects.create(customer=customer, msisdn=msisdn,
                                                customer_account=data.customer_account,
                                                amount=data.amount, session_id=session,
                                                transaction_type="Data Self")
                    message = "END An error has occurred, please try again later"
                    close_session(session)
            else:
                data.pin_tries += 1
                data.save()
                message = transaction_pin_reties(data, session)
                session.current_screen = "confirm_ussd_for_data_others"
                session.save()
                send_response(port, msisdn, text, session_id, message)
                return Response({"message": message})

            send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})
        # <<<<<<<<<<<<<<---------------------- Buy Data Others Ends ------------------------------------->>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<---------------------- CHANGE PIN MENU BEGINS ------------------------->>>>>>>>>>>>>>>>>>>
        elif current_screen == 'change_pin_request':
            message = screens.change_pin_request_screen(text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'enter_new_pin_change_pin':
            message = screens.enter_new_pin_change_pin_screen(text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'enter_new_pin_change_pin_confirm':
            message = screens.enter_new_pin_change_pin_confirm_screen(text, session, customer_pin)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<<<<<<<<---------------------- CHANGE PIN MENU END ----------------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<---------------------- RESET PIN MENU BEGINS --------------------------->>>>>>>>>>>>>>>>>>>

        elif current_screen == 'reset_pin_request':
            message = screens.reset_pin_request_screen(session, text, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'reset_pin_enter_acct_number':
            message = screens.reset_pin_enter_acct_number_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'reset_pin_enter_debit_card' or current_screen == 'reset_pin_enter_token':
            message = screens.card_or_token_input_screen(customer, text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'reset_pin_enter_new_pin':
            message = screens.reset_pin_enter_new_pin_screen(text, customer_pin, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'reset_pin_retype_pin':
            message = screens.reset_pin_retype_pin_screen(customer_pin, text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<<<<<<<<------------------------- RESET PIN MENU END --------------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<-------------------- BLOCK ACCOUNT MENU BEGINS ------------------------->>>>>>>>>>>>>>>>>>>
        elif current_screen == 'block_account_request':
            message = screens.block_account_request_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'block_account_confirm_or_cancel':
            message = screens.block_account_confirm_or_cancel_screen(text, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        elif current_screen == 'block_account_enter_pin':
            message = screens.block_account_enter_pin_screen(text, customer_pin, customer, session)
            send_response(port, msisdn, text, session_id, message)
            return Response({'message': message})

        # <<<<<<<<<<<<<<<<-------------------- BLOCK ACCOUNT MENU END ------------------------->>>>>>>>>>>>>>>>>>>

        # <<<<<<<<<<<<<<<<-------------------- INCREASE LIMIT MENU BEGIN ------------------------->>>>>>>>>>>>>>>>>>>
        elif current_screen == 'limit_agreement':
            if text == "1":
                all_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
                message = responses.limit_select_account(all_accounts)
                session.current_screen = 'limit_select_account'
                session.save()
            elif text == "2":
                message = responses.main_menu_second_page()
                session.current_screen = 'main_menu_second_page'
                session.save()
            else:
                message = responses.limit_agreement()
                session.current_screen = 'limit_agreement'
                session.save()
            return message

        elif current_screen == 'limit_select_account':
            message = responses.limit_card_or_otp()
            session.current_screen = 'limit_card_or_otp'
            session.save()
        # <<<<<<<<<<<<<<<<-------------------- INCREASE LIMIT MENU END ------------------------->>>>>>>>>>>>>>>>>>>

        # <<< ------------------------------ Airtime Self -------------------------------------

        elif current_screen == "airtime_amount_self":
            """
                Info: After entering amount to buy, here we:
                1. fetched the account(s) of user for Account Selection in the next page.
            """
            if text.isnumeric() and text > "0":
                # Add amount to Airtime Instance
                Airtime.objects.create(
                    session=session, customer=customer, purchase_type="self", amount=text
                )

                # Fetch customer's accounts and give response
                customer_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
                message = responses.select_account(customer_accounts)
                session.current_screen = "select_account"
            else:
                message = responses.airtime_amount_self()
                session.current_screen = 'airtime_amount_self'

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "select_account":
            """ Expect text to be a numeric number 1 to n, depending on the numbers of account this customer has. """
            # Actions :
            # 1. Get the account number as selected by the user.
            # 2. Get the account balance of the selected account.
            try:
                selected_account = CustomerAccount.objects.get(customer=customer, position=text)
                if selected_account is not None:
                    airtime_ins = Airtime.objects.filter(customer=customer, session=session, status="pending",
                                                         purchase_type="self").last()
                    airtime_ins.customer_account = selected_account
                    airtime_ins.beneficiary = msisdn
                    airtime_ins.save()

                    # Check if the selected account has sufficient funds (!! charges !!)
                    # Call API to check account balance or Maybe we also saved customer's account balance.
                    response = balance_enquiry(selected_account.account_no)

                    customer_balance = 0
                    if response["responseCode"] == "00":
                        customer_balance = decimal.Decimal(response["balance"])
                        if customer_balance < decimal.Decimal(airtime_ins.amount):
                            message = responses.no_sufficient_funds()
                            session.current_screen = "no_sufficient_funds"
                            session.save()

                    if customer_balance > decimal.Decimal(airtime_ins.amount) and airtime_ins.amount > 1:
                        description = f"Ref. {session_id} Top-up IFO {response['accountName']} " \
                                      f"{msisdn} {selected_account.account_no}"
                        fund_transfer_response = fund_transfer_others_local(
                            session_id=session_id, sender_acct=selected_account.account_no, receiver_acct=0000000000,
                            amount=airtime_ins.amount, narration=description, charges=decimal.Decimal(0.0),
                            channel_code=3, sender_phone=msisdn, sender_balance=customer_balance
                        )

                        if fund_transfer_response['responseCode'] == "00":
                            # call top-up api to top up customer
                            bill_payment_response = bill_payment_cable_tv(
                                email="", phone_no=msisdn, payment_code="10401", amount=airtime_ins.amount,
                                customer_id=msisdn, payment_type="VTUP"
                            )

                            if bill_payment_response["responseCode"] == "00":
                                message = responses.airtime_self_purchase_success(airtime_ins)
                                send_response(port, msisdn, text, session_id, message)
                                session.current_screen = "airtime_self_purchase_success"
                                session.save()
                                airtime_ins.status = "success"
                                airtime_ins.save()

                            else:
                                # Log reversal
                                FundReversal.objects.create(
                                    customer=customer, msisdn=msisdn, customer_account=airtime_ins.customer_account,
                                    amount=airtime_ins.amount, session_id=session, transaction_type="airtime self"
                                )

                        elif fund_transfer_response['responseCode'] == '25':
                            # response_nip_transaction_status = nip_transaction_status(session_id=session_id, channel_code=7)
                            # call nip_transaction_status-tsq after 5mins How the 5 minutes timing would work: Create a model that
                            # keeps the records going into the tsq including session_id the model would have fields: time to
                            # run, status, ran?-> True or False

                            FundReversal.objects.create(
                                customer=customer, msisdn=msisdn, customer_account=airtime_ins.customer_account,
                                amount=airtime_ins.amount, session_id=session, transaction_type="airtime self"
                            )
                        else:
                            message = "END An error has occurred while charging your account, please try again later"
                            # airtime_ins.status = "failed"
                            # airtime_ins.save()
                            send_response(port, msisdn, text, session_id, message)
                            close_session(session)
                        return Response({"message": message})
                else:
                    customer_accounts = CustomerAccount.objects.filter(customer=customer).order_by("id")
                    message = responses.select_account(customer_accounts)
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "select_account"
                    session.save()
                send_response(port, msisdn, text, session_id, message)
                return Response({"message": message})
            except Exception as err:
                log_errors(f"Error message: {err}")
                return Response({"message": "An error has occurred, please try again later"})

        # -------------------------- Airtime-Self End --------------------------->

        # -------------------------- Airtime-Others Start-----------------------------

        elif current_screen == "airtime_others_receiver_number":
            receiver_number = f"0{text[-10:]}"
            Airtime.objects.create(
                customer=customer, session=session, purchase_type="others", beneficiary=receiver_number
            )
            if not receiver_number.isnumeric() or len(receiver_number) != 11:
                message = responses.airtime_others_receiver_number()
                session.current_screen = 'airtime_others_receiver_number'
            else:
                message = responses.airtime_amount_others()
                session.current_screen = 'airtime_amount_others'
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "airtime_amount_others":
            if not text.isnumeric():
                # wrong input returns the response back to the user.
                message = responses.airtime_amount_others()
                session.current_screen = 'airtime_amount_others'
            else:
                # Save the amount to airtime_instance
                airtime_inst = Airtime.objects.filter(customer=customer, session=session, purchase_type="others").last()
                airtime_inst.amount = text
                airtime_inst.save()
                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.select_account_for_airtime_other(customer_account=customer_account.order_by("id"))
                session.current_screen = f'select_account_for_airtime_other'
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen == "airtime_others_select_network":
            message = screens.select_mno_screen(customer, text, session, "airtime")
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen == "select_account_for_airtime_other":
            if CustomerAccount.objects.filter(customer=customer, position=text).exists():
                selected_account = CustomerAccount.objects.get(customer=customer, position=text)
                airtime_inst = Airtime.objects.filter(customer=customer, session=session, purchase_type="others").last()
                airtime_inst.customer_account = selected_account
                airtime_inst.save()
                # Call Jaiz API for to get account balance
                balance_response = balance_enquiry(selected_account.account_no)

                if balance_response["responseCode"] == "00":
                    if decimal.Decimal(balance_response["balance"]) >= decimal.Decimal(
                            airtime_inst.amount) and airtime_inst.amount > 1:
                        # Call LookUp API
                        look_up = False
                        if look_up is False:
                            message = responses.select_mobile_network()
                            session.current_screen = 'airtime_others_select_network'
                            send_response(port, msisdn, text, session_id, message)
                            session.save()
                            return Response({"message": message})
                        mno = "9mobile"  # MNO from LOOKUP
                        airtime_inst.network = mno
                        airtime_inst.save()
                        message = responses.airtime_others_confirm_pin(
                            beneficiary=airtime_inst.beneficiary, amount=airtime_inst.amount, network=mno
                        )
                        session.current_screen = "airtime_others_confirm_pin"
                    else:
                        message = responses.no_sufficient_funds()
                        session.current_screen = "no_sufficient_funds"
                    send_response(port, msisdn, text, session_id, message)
                    session.save()
                    return Response({"message": message})

            customer_account = CustomerAccount.objects.filter(customer=customer).order_by("id")
            message = responses.select_account_for_airtime_other(customer_account=customer_account)
            send_response(port, msisdn, text, session_id, message)
            session.current_screen = f'select_account_for_airtime_other'
            session.save()
            return Response({"message": message})

        elif session.current_screen == "airtime_others_confirm_pin":
            airtime = Airtime.objects.filter(customer=customer, session=session).last()
            if decrypt_text(customer_pin.pin) != text or text == "0":
                airtime.pin_tries += 1
                airtime.save()
                message = transaction_pin_reties(airtime, session)
                session.current_screen = "airtime_others_confirm_pin"
                session.save()
                send_response(port, msisdn, text, session_id, message)
                return Response({"message": message})

            balance_response = balance_enquiry(airtime.customer_account.account_no)

            # Call Fund Transfer to debit customer.
            fund_transfer_response = fund_transfer_others_local(
                session_id=session_id, sender_acct=airtime.customer_account.account_no, receiver_acct=0000000000,
                amount=airtime.amount,
                narration=f"Ref. {session_id} Top-up IFO {balance_response['accountName'].split(' ')[0]} {msisdn} {airtime.customer_account.account_no}",
                charges=decimal.Decimal(0.0), channel_code=settings.AIRTIME_AND_DATA_CHANNEL_CODE, sender_phone=msisdn,
                sender_balance=balance_response["balance"]
            )

            if fund_transfer_response['responseCode'] == "00":
                # call top-up api to top up customer
                bill_payment_response = bill_payment_cable_tv(
                    email="", phone_no=msisdn, payment_code="10401", amount=airtime.amount, customer_id=msisdn,
                    payment_type="VTUP"
                )

                if bill_payment_response["responseCode"] == "00":
                    message = responses.airtime_self_purchase_success(airtime)
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "airtime_other_purchase_success"
                    session.save()
                    airtime.status = "success"
                    airtime.save()

                elif fund_transfer_response['responseCode'] == '25':
                    # response_nip_transaction_status = nip_transaction_status(session_id=session_id, channel_code=7)
                    # call nip_transaction_status-tsq after 5mins How the 5 minutes timing would work: Create a model that
                    # keeps the records going into the tsq including session_id the model would have fields: time to
                    # run, status, ran?-> True or False

                    FundReversal.objects.create(
                        customer=customer, customer_account=airtime.customer_account, msisdn=msisdn,
                        amount=airtime.amount, session_id=session, transaction_type="airtime other",
                        beneficiary=airtime.beneficiary
                    )
                    message = "CON Error processing request, please try again later.\n\n0. Main Menu"
                    airtime.status = "failed"
                    airtime.save()
                    send_response(port, msisdn, text, session_id, message)
            else:
                message = "CON Error processing request, please try again later.\n\n0. Main Menu"
                airtime.status = "failed"
                airtime.save()
                send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})

        # --------------------- Airtime-Others END ----------- >

        # --------------------- Jaiz to Jaiz Transfer Starts --------------------------------->

        elif current_screen == "transfer_jaiz_acct" or current_screen == "incorrect_acct_number":
            if not (text.isnumeric() and len(text) == 10):
                message = responses.transfer_jaiz_acct()
                session.current_screen = "transfer_jaiz_acct"
            else:
                # Check if account number is valid
                local_name_response = name_enquiry_local(account_no=text)
                if local_name_response["responseCode"] != "00":
                    # Incorrect account number, please enter correct account number to proceed
                    message = responses.incorrect_acct_number()
                    session.current_screen = "incorrect_acct_number"
                else:
                    # Save Beneficiary account to FundTransfer model
                    receiver = local_name_response['accountName']
                    FundTransfer.objects.create(
                        customer=customer, session=session, transfer_type="jaiz", account_no=text, bank="Jaiz Bank",
                        bank_selected="Jaiz Bank", receiver_name=receiver
                    )
                    # Next Page - Enter Amount
                    message = responses.request_amount_to_transfer()
                    session.current_screen = "request_amount_to_transfer"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "request_amount_to_transfer":
            if not text.isnumeric():
                message = responses.request_amount_to_transfer()
                session.current_screen = "request_amount_to_transfer"
            else:
                # Update Fund Transfer model
                fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, status="pending").last()
                fund_transfer.amount = text
                fund_transfer.save()

                # Next page - Select Account
                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.jaiz_transfer_select_account(customer_account)
                session.current_screen = "jaiz_transfer_select_account"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "jaiz_transfer_select_account":
            # check if account has enough balance
            customer_account = CustomerAccount.objects.filter(customer=customer, position=text)
            if customer_account is not None:
                customer_account = CustomerAccount.objects.get(customer=customer, position=text)
                fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, status="pending").last()
                fund_transfer.customer_account = customer_account
                fund_transfer.save()
                selected_account = customer_account.account_no
                # Check if customer has enough funds for transfer
                balance_enquiry_response = balance_enquiry(account_no=selected_account)

                if decimal.Decimal(fund_transfer.amount) > decimal.Decimal(balance_enquiry_response["balance"]):
                    # if transfer amount is greater than account bals., render Insufficient Funds.
                    message = responses.no_sufficient_funds()
                    fund_transfer.status = 'failed'
                    fund_transfer.save()
                    session.current_screen = "no_sufficient_funds"
                    send_response(port, msisdn, text, session_id, message)
                else:
                    message = responses.confirm_funds_transfer(fund_transfer)
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "confirm_funds_transfer"
                    session.save()
            else:
                # Return user back to select account
                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.jaiz_transfer_select_account(customer_account)
                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "jaiz_transfer_select_account"
                session.save()
            return Response({"message": message})

        elif current_screen == "confirm_funds_transfer":
            fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, status="pending").last()
            if text.isnumeric and len(text) == 4 and text == decrypt_text(customer_pin.pin):
                name_enquiry_response = name_enquiry_local(fund_transfer.customer_account.account_no)
                account_balance_response = balance_enquiry(fund_transfer.customer_account.account_no)
                description = f"Ref. {session_id} Top-up IFO {name_enquiry_response['accountName'].split(' ')[0]} " \
                              f"{msisdn} {fund_transfer.customer_account.account_no}"
                fund_transfer_response = fund_transfer_others_local(
                    session_id=session_id, sender_acct=fund_transfer.customer_account.account_no,
                    receiver_acct=fund_transfer.account_no, amount=fund_transfer.amount, narration=description,
                    charges=decimal.Decimal(settings.CHARGES), channel_code=settings.INTRA_BANK_TRANSFER_CHANNEL_CODE,
                    sender_phone=msisdn, sender_balance=account_balance_response["balance"]
                )

                if fund_transfer_response['responseCode'] == "00":
                    # Successful Jaiz transfer
                    message = responses.jaiz_transfer_confirmed(fund_transfer=fund_transfer)
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "jaiz_to_jaiz_transfer_success"
                    session.save()
                    fund_transfer.status = "success"
                    fund_transfer.save()

                elif fund_transfer_response['responseCode'] == '25':
                    # call nip_transaction_status-tsq after 5mins.
                    # How the 5 minutes timing would work: Create a model that keeps the records going into the tsq
                    # including session_id the model would have fields: status, ran?-> True or False

                    FundReversal.objects.create(
                        customer=customer, customer_account=fund_transfer.customer_account, msisdn=msisdn,
                        amount=fund_transfer.amount, session_id=session, transaction_type="jaiz fund transfer",
                        beneficiary=fund_transfer.beneficiary
                    )
                    message = "END An error has occurred, please try again later"
                    send_response(port, msisdn, text, session_id, message)
                    close_session(session)
                return Response({"message": message})

            else:
                fund_transfer.pin_tries += 1
                fund_transfer.save()
                message = responses.transaction_pin_reties(fund_transfer, session)
                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "confirm_funds_transfer"
                send_response(port, msisdn, text, session_id, message)
                return Response({"message": message})

        # ----------------------- JAIZ TO JAIZ TRANSFER END---------------------------------------->

        #   ---------------------- Fund Transfer Others Start ---------------->
        elif current_screen == "others_account_number" or current_screen == "trnsf_others_incorrect_acct_no":
            if text.isnumeric and len(text) == 10:

                # Check if bank number is correct
                fund_transfer = FundTransfer.objects.create(
                    customer=customer, session=session, transfer_type="others", account_no=text, next=1
                )

                message = responses.enter_beneficiary_bank(account_number=text, session=session, customer=customer,
                                                           instance=fund_transfer)
                session.current_screen = "enter_beneficiary_bank"

            else:
                message = responses.others_account_number()
                session.current_screen = "others_account_number"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "enter_beneficiary_bank":
            fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, status="pending", transfer_type="others").last()
            if not text.isnumeric() or 0 > int(text) or int(text) > len(fund_transfer.bank_list_response):
                session.current_screen = "others_account_number"
                message = responses.others_account_number()
                send_response(port, msisdn, text, session_id, message)
                session.save()
                return Response({"message": message})

            if text == "00":
                fund_transfer.bank_selected = f"{text}"
                fund_transfer.next = fund_transfer.next + 1
                fund_transfer.save()

                message = responses.enter_beneficiary_bank(account_number=fund_transfer.account_no, session=session,
                                                           customer=customer, instance=fund_transfer)

                if message is False:
                    message = responses.others_account_number()
                    session.current_screen = "others_account_number"
                    send_response(port, msisdn, text, session_id, message)
                    session.save()
                    return Response({"message": message})

                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "enter_beneficiary_bank"
                session.save()
                return Response({"message": message})

            bank_selected_digit = fund_transfer.bank_selected
            bank = str(list(fund_transfer.bank_list_response)[int(text) - 1]).split(".")[1]

            fund_transfer.bank = bank
            fund_transfer.bank_selected = text
            fund_transfer.save()

            ##################################################################################
            # Action: Check if the account selected is also valid in the bank selected also. #
            ##################################################################################
            bank_code = str(list(fund_transfer.bank_list_response)[int(text) - 1]).split(".")[3]
            confirm_bank_account_response = interbank_name_enquiry(
                session_id=session.session_id, bank_code=bank_code, account_no=fund_transfer.account_no,
                channel_code=settings.INTER_BANK_TRANSFER_CHANNEL_CODE
            )
            if confirm_bank_account_response["NESingleResponse"]["ResponseCode"] == "00":
                account_name = confirm_bank_account_response["NESingleResponse"]["AccountName"]
                fund_transfer.receiver_name = account_name
                fund_transfer.save()
                message = responses.fund_transfer_amount()
                session.current_screen = "fund_transfer_amount"
            else:
                message = responses.trnsf_others_incorrect_acct_no()
                session.current_screen = "trnsf_others_incorrect_acct_no"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "fund_transfer_amount":
            if text.isnumeric():
                funds_transfer = FundTransfer.objects.filter(customer=customer, session=session, transfer_type="others", status="pending").last()
                funds_transfer.amount = text
                funds_transfer.save()

                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.jaiz_transfer_others_select_account(customer_account)
                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "jaiz_transfer_others_select_account"
            else:
                message = responses.fund_transfer_amount()
                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "fund_transfer_amount"
            session.save()
            return Response({"message": message})

        elif session.current_screen == "jaiz_transfer_others_select_account":
            try:
                customer_account = CustomerAccount.objects.get(customer=customer, position=text)
                fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, transfer_type="others", status="pending").last()
                fund_transfer.customer_account = customer_account
                fund_transfer.save()

                # check if user has enough balance
                balance_response = balance_enquiry(fund_transfer.customer_account.account_no)

                if balance_response["responseCode"] == "00":
                    if decimal.Decimal(balance_response["balance"]) >= decimal.Decimal(
                            fund_transfer.amount) and fund_transfer.amount > 1:
                        message = responses.confirm_funds_transfer_others(fund_transfer)
                        session.current_screen = "confirm_funds_transfer_others"
                    else:
                        message = responses.no_sufficient_funds()
                        session.current_screen = "no_sufficient_funds"
                        send_response(port, msisdn, text, session_id, message)
                        session.save()
                        close_session(session)
                        return Response({"message": message})
                else:
                    message = responses.jaiz_transfer_others_select_account(customer_account)
                    session.current_screen = "jaiz_transfer_others_select_account"
                send_response(port, msisdn, text, session_id, message)
                session.save()
                return Response({"message": message})
            except (Exception,) as err:
                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.jaiz_transfer_others_select_account(customer_account)
                session.current_screen = "jaiz_transfer_others_select_account"
                send_response(port, msisdn, text, session_id, message)
                session.save()
                log_errors(err)
                return Response({"message": message})
        # --------------------------- Confirm Fund Transfer Others ------------------->

        elif current_screen == "confirm_funds_transfer_others":
            fund_transfer = FundTransfer.objects.filter(customer=customer, session=session, status="pending", transfer_type="others").last()
            if text.isnumeric and len(text) == 4 and text == decrypt_text(customer_pin.pin):

                account_balance_response = balance_enquiry(fund_transfer.customer_account.account_no)
                bank_selected_digit = fund_transfer.bank_selected
                bank_code = str(list(fund_transfer.bank_list_response)[int(bank_selected_digit) - 1]).split(".")[3]

                confirm_bank_account_response = interbank_name_enquiry(
                    session_id=session.session_id, bank_code=bank_code, account_no=fund_transfer.account_no,
                    channel_code=settings.INTER_BANK_TRANSFER_CHANNEL_CODE
                )
                fund_transfer_response = nip_fund_transfer(
                    session_id=session_id, name_enq_ref="", bank_code=bank_code,
                    narration=f"Ref. {session_id} IFO {bank_code} {confirm_bank_account_response['NESingleResponse']['AccountName']}",
                    amount=fund_transfer.amount, channel_code=settings.INTER_BANK_TRANSFER_CHANNEL_CODE,
                    beneficiary_acct_name=confirm_bank_account_response['NESingleResponse']['AccountName'],
                    beneficiary_acct_no=confirm_bank_account_response["NESingleResponse"]["AccountNumber"],
                    beneficiary_bvn_no=confirm_bank_account_response["NESingleResponse"]["BankVerificationNumber"],
                    beneficiary_kyc="", sender_acct_name=account_balance_response["accountName"],
                    sender_acct_no=fund_transfer.customer_account.account_no, sender_kyc="", payment_ref=""
                )

                if fund_transfer_response['FTSingleResponse']['ResponseCode'] == "00":
                    # Successful Jaiz transfer
                    message = responses.jaiz_transfer_confirmed(fund_transfer=fund_transfer)
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "other_bank_transfer_success"
                    session.save()
                    fund_transfer.status = "success"
                    fund_transfer.save()

                elif fund_transfer_response['responseCode'] == '25':
                    # call nip_transaction_status-tsq after 5mins.
                    # How the 5 minutes timing would work: Create a model that keeps the records going into the tsq
                    # including session_id the model would have fields: status, ran?-> True or False

                    FundReversal.objects.create(
                        customer=customer, customer_account=fund_transfer.customer_account, msisdn=msisdn,
                        amount=fund_transfer.amount, session_id=session, transaction_type="fund transfer others",
                        beneficiary=fund_transfer.beneficiary
                    )
                    message = "END An error has occurred, please try again later"
                    close_session(session)
                    send_response(port, msisdn, text, session_id, message)
                return Response({"message": message})

            else:
                fund_transfer.pin_tries += 1
                fund_transfer.save()
                message = responses.transaction_pin_reties(fund_transfer, session)
                send_response(port, msisdn, text, session_id, message)
                session.current_screen = "confirm_funds_transfer_others"
            return Response({"message": message})
        # ------------------------------ FUND TRANSFER OTHERS END ---------------------------------------------->

        # --------------------- Account Balance Starts --------------------------------->
        elif current_screen == "account_balance_select_acct":
            try:
                selected_account = CustomerAccount.objects.get(customer=customer, position=text)

                if selected_account:
                    # Perform Action to get customer's account balance for the selected account number
                    message = responses.confirm_ussd_account_balance()
                    session.current_screen = f"confirm_ussd_account_balance-{text}"
                else:
                    customer_account = CustomerAccount.objects.filter(customer=customer)
                    message = responses.account_balance_select_acct(customer_account)
                    session.current_screen = "account_balance_select_acct"
                send_response(port, msisdn, text, session_id, message)
                session.save()
                return Response({"message": message})
            except (Exception,) as err:
                close_session(session)
                log_errors(err)
                return Response({"message": str(err)})

        elif current_screen[0:28] == "confirm_ussd_account_balance":
            account_position = session.current_screen.split('-')[1]

            customer_account = CustomerAccount.objects.get(customer=customer, position=account_position)
            if text.isnumeric and len(text) == 4 and text == decrypt_text(customer_pin.pin):
                # ACTION: Call API to check customer balance.
                account_balance_response = balance_enquiry(customer_account.account_no)

                if account_balance_response["responseCode"] == "00":
                    message = responses.account_balance_msg(account_balance_response["balance"])
                    send_response(port, msisdn, text, session_id, message)
                    session.current_screen = "account_balance_msg"
                    session.save()
                else:
                    message = "CON Error fetching balance, please try again later\n\n0. Main Menu"
                    send_response(port, msisdn, text, session_id, message)
            else:
                message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
                send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})

        # ----------------------- Second Menu Page Starts ----------------------------->
        elif current_screen == "main_menu_second_page":
            message = screens.main_menu_second_page_screen(text, session, customer)
            send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})

        #   -----------------2 Facility Balance Starts ----------------------------------->
        elif current_screen == "facility_balance_pin":
            if text.isnumeric and len(text) == 4 and text == decrypt_text(customer_pin.pin):
                message = responses.facility_balance_unavailable()
                session.current_screen = "facility_balance_unavailable"
            else:
                message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        #   -----------------p2 - 7 Opt Out Starts ----------------------------------->
        elif current_screen == "confirm_pin_to_opt_out":
            if text.isnumeric and len(text) == 4 and text == decrypt_text(customer_pin.pin):
                # ACTION: OPT Customer OUT (change customer onboard status to False)
                # Then perform a check from the first process of the program.

                customer.active = False
                customer.save()

                message = responses.opt_out_successful(customer)
                session.current_screen = "opt_out_successful"
                close_session(session)
            else:
                message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
                session.current_screen = "confirm_pin_to_opt_out"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        #   ------------------------------- Bill Payment Cable TV ----------------------------------->
        elif current_screen == "pay_bills_option_page":
            try:
                bill_category = BillCategory.objects.get(id=text)
                message, marker = responses.category_packages(bill_category, customer, session, next=text)
                session.current_screen = f"category_packages_{bill_category.id}_{marker}"

            except (Exception,) as err:
                message = responses.pay_bills_option()
                session.current_screen = "pay_bills_option_page"
                log_errors(err)
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen[0:18] == "category_packages_":
            # 1. slice the value of 'session.current_screen' to get BillCat. ID that was selected in the last page.
            cat_id, marker = session.current_screen.split("_")[2], session.current_screen.split("_")[3]
            try:
                bill_category = BillCategory.objects.get(id=cat_id)
                #  This allows user to goback to the 'category_packages_2_TV' screen.
                # if text == "99":
                #     message, marker = responses.category_packages(bill_category, customer=customer, session=session,
                #                                                   next=text)
                if text == "00":
                    message, marker = responses.category_packages(bill_category, customer=customer, session=session,
                                                                  next=text)
                elif text == "2":
                    print('--------- Here ---------')
                    message, marker = responses.category_packages(bill_category, customer=customer, session=session,
                                                                  next=text)
                else:
                    print('-----------else------------')
                    message, marker, success = screens.detect_cat_and_select_item(text=text, customer=customer,
                                                                                  session=session, marker=marker)
                    # session.current_screen = "item_list"

                    if not success:
                        message, marker = responses.category_packages(bill_category, customer=customer, session=session,
                                                                      next=text)
                        session.current_screen = f"category_packages_{bill_category.id}_{marker}"

            except (Exception,) as err:
                bill_category = BillCategory.objects.get(id=cat_id)
                message, marker = responses.category_packages(bill_category, customer=customer, session=session,
                                                              next=text)
                session.current_screen = f"category_packages_{bill_category.id}_{marker}"
                log_errors(err)

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif session.current_screen[:10] == "item_list_":
            biller_id, marker = session.current_screen.split("_")[2], session.current_screen.split("_")[3]

            try:
                item = Item.objects.get(id=text, biller_id=biller_id)
                if marker == "EL":
                    instance = Electricity.objects.get(customer=customer, session=session, status="pending")
                    message = responses.enter_meter_no(item_name=item.name)
                    session.current_screen = "enter_meter_no"

                elif marker == "TV":
                    instance = CableSubscription.objects.get(customer=customer, session=session, status="pending")
                    message = responses.enter_customer_number_cable_tv()
                    session.current_screen = "enter_customer_number_cable_tv"

                instance.item = item
                instance.save()
            except (Exception,) as err:
                message = responses.pay_bills_option()
                session.current_screen = "pay_bills_option_page"
                log_errors(err)

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        # -------------------------- END OF BILL PAYMENT --------------------------------------------->

        # ------------------------- ADD OR REMOVE ACCOUNT ------------------------------------------->
        elif current_screen == "add_or_remove_account":
            if text.isnumeric() and text == "1":
                message = responses.enter_acct_to_add()
                session.current_screen = "enter_acct_to_add"
            elif text.isnumeric() and text == "2":
                customer_account = CustomerAccount.objects.filter(customer=customer)
                message = responses.select_acct_for_removal(customer_account)
                session.current_screen = "select_acct_for_removal"
            else:
                message = responses.add_or_remove_account()
                session.current_screen = "add_or_remove_account"
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        #   --------------------------- ADD ACCOUNT (COMPLETED)-------------------------------------------------

        elif current_screen == "enter_acct_to_add":
            if text.isnumeric() and len(text) == 10:
                # There could be an error here, because we checked if the account to be added has the same Phone Number
                # as the msisdn which dials the code. (A BVN check can be used here instead of Phone number check but,
                # Jaiz Official Flow requires we perform a Phone Number Check)

                name_enquiry_response = name_enquiry_local(text)
                phone_number_check = str(msisdn[-10:]) == str(name_enquiry_response["phoneNo"])[-10:]
                if name_enquiry_response["responseCode"] == "00" and phone_number_check:
                    # check if acct no. has been added already
                    list_of_accts = [acct.account_no for acct in CustomerAccount.objects.filter(customer=customer)]
                    if text in list_of_accts:
                        message = responses.acct_already_exist()
                        session.current_screen = "acct_already_exist"
                        send_response(port, msisdn, text, session_id, message)
                        session.save()
                        return Response({"message": message})

                    # Give a position to the new acct by getting the pos. of the last acct and increment it by 1.
                    cus_last_acct_position_number = CustomerAccount.objects.filter(customer=customer).last()
                    new_account_position = int(cus_last_acct_position_number.position) + 1

                    CustomerAccount.objects.create(customer=customer, account_no=text, position=new_account_position)

                    # Confirm to add Account
                    message = responses.confirm_to_add_acct(
                        acct_no=text, acct_name=name_enquiry_response["accountName"])

                    session.current_screen = "confirm_to_add_acct"
                else:
                    message = responses.add_wrong_number_msg()
            else:
                message = responses.enter_acct_to_add()
                session.current_screen = "enter_acct_to_add"

            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "confirm_to_add_acct":
            if text.isnumeric() and len(text) == 4 and text == decrypt_text(customer_pin.pin):
                message = responses.successfully_added_acct()
                session.current_screen = "successfully_added_acct"
                session.save()
            else:
                message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
            send_response(port, msisdn, text, session_id, message)
            return Response({"message": message})
        # --------------------- END OF ADD ACCOUNT -------------------------------

        # --------------------- Remove Account (COMPLETED) ----------------------------------
        elif current_screen == "select_acct_for_removal":
            customer_accounts = CustomerAccount.objects.filter(customer=customer)
            customer_account = None
            try:
                customer_account = CustomerAccount.objects.get(customer=customer, position=text)
                if text.isnumeric():
                    if customer_accounts.count() < 2:
                        message = "You have one account, kindly add another one before removing this\n\n0. Main Menu"
                        session.current_screen = "select_acct_for_removal"
                        session.save()
                        send_response(port, msisdn, text, session_id, message)
                        return Response({"message": message})
                    message = responses.warning_account_removal(customer_account)
                    session.current_screen = "warning_account_removal"
                    customer_account.request_removal = True
                else:
                    message = responses.select_acct_for_removal(customer_accounts)
                    session.current_screen = "select_acct_for_removal"
                    customer_account.request_removal = False

            except (Exception,) as err:
                message = responses.select_acct_for_removal(customer_accounts)
                session.current_screen = "select_acct_for_removal"
                customer_account.request_removal = False
                log_errors(err)

            customer_account.save()
            send_response(port, msisdn, text, session_id, message)
            session.save()
            return Response({"message": message})

        elif current_screen == "warning_account_removal":
            customer_account = CustomerAccount.objects.filter(customer=customer, request_removal=True)
            if text == decrypt_text(customer_pin.pin):
                # ACTION: remove this customer's account
                for acct in customer_account:
                    acct.delete()
                message = responses.account_removal_success()
                session.current_screen = "account_removal_success"
                session.save()
            else:
                message = "CON Invalid PIN, please enter correct PIN\n\n0. Main Menu"
                send_response(port, msisdn, text, session_id, message)
                # turn off request_removal
                for acct in customer_account:
                    acct.request_removal = False
                    acct.save()
            return Response({"message": message})
        # ----- END OF REMOVE ACCOUNT ------------------------------------------------------->
        return Response({})
