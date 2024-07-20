from home import api
from home.models import FundReversal


def perform_bank_update_cron():
    pass


def fund_reversal():
    # Called After 5 Minutes

    fund_reversals = FundReversal.objects.filter(has_ran=False)
    if fund_reversals is not None:
        for fund_rev in fund_reversals:
            fund_rev = FundReversal.objects.get(id=fund_rev.id)

            response_nip_transaction_status = api.nip_transaction_status(session_id=fund_rev.session_id.session_id,
            channel_code=7)

            # response_nip_transaction_status = {
            #     "TSQuerySingleResponse": {
            #         "SourceInstitutionCode": "000006", "ChannelCode": "7",
            #         "SessionID": "000006181225000017000000000001",
            #         "ResponseCode": "00"
            #     }
            # }
            if response_nip_transaction_status["ResponseCode"] == "00":
                # If "ResponseCode" is "00" that means user was debited.
                # if tsq returns 00 then call log reversal
                response_nip_log_reversal = api.nip_log_reversal(session_id=fund_rev.session_id.session_id)
                if response_nip_log_reversal["responseCode"] == "00":
                    fund_rev.has_ran = True
                    fund_rev.save()
                    print("-------------------------------- Called for reversal -------------------------------------")
