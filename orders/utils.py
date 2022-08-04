import uuid
from datetime import datetime
from stripe import BalanceTransaction

class ExchangeRate(object):
    
    def get_exchange_rate_and_fee(charge):
        try:
            balance_transaction = charge['balance_transaction'] or charge.getBalanceTransaction()
            balanceTransaction = BalanceTransaction.retrieve(balance_transaction)
            exchange_rate = balanceTransaction.getExchangeRate()
            transaction_fee = balanceTransaction['fee']
            if isinstance(float(exchange_rate), float) or isinstance(float(transaction_fee),float):
                # return {"exchange_rate":float(exchange_rate),"transaction_fee": float(transaction_fee)}
                return {"status":True,"exchange_rate":float(650.00),"transaction_fee": float(2.980)}
            
            return {"status":False}
        except:
            return {"status":False}

    

def get_currrent_date_time():
    
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
    
    
def get_sample_response():
  
    return {
            "id": str(uuid.uuid4()),
            "object": "charge",
            "amount": 2000,
            "amount_captured": 0,
            "amount_refunded": 0,
            "application": "null",
            "application_fee": "null",
            "application_fee_amount": "null",
            "balance_transaction": "txn_1032HU2eZvKYlo2CEPtcnUvl",
            "billing_details": {
                "address": {
                "city": "null",
                "country": "null",
                "line1": "null",
                "line2": "null",
                "postal_code": "null",
                "state": "null"
                },
                "email": "null",
                "name": "Eko Emmanuel Upo",
                "phone": "null"
            },
            "calculated_statement_descriptor": "null",
            "captured": False,
            "created": 1658761038,
            "currency": "usd",
            "customer": "null",
            "description": "My First Test Charge (created for API docs at https://www.stripe.com/docs/api)",
            "disputed": False,
            "failure_balance_transaction": "null",
            "failure_code": "null",
            "failure_message": "null",
            "fraud_details": {},
            "invoice": "null",
            "livemode": False,
            "metadata": {},
            "on_behalf_of": "null",
            "outcome": "null",
            "paid": True,
            "payment_intent": "null",
            "payment_method": "card_1LO1yv2eZvKYlo2CG5btrOkZ",
            "payment_method_details": {
                "card": {
                "checks": {
                    "address_line1_check": "null",
                    "address_postal_code_check": "null",
                    "cvc_check": "null"
                },
                "country": "US",
                "exp_month": 7,
                
                "exp_month": "11",
                "exp_year": "2024",
                "brand": "Master card",
                                    
                "fingerprint": "Xt5EWLLDS7FJjR1c",
                "funding": "credit",
                "installments": "null",
                "last4": "4242",
                "mandate": "null",
                "moto": "null",
                "network": "visa",
                "three_d_secure": "null",
                "wallet": "null"
                },
                "type": "card"
            },
            "receipt_email": "null",
            "receipt_number": "null",
            "receipt_url": "https://pay.stripe.com/receipts/acct_1032D82eZvKYlo2C/ch_3LPSig2eZvKYlo2C1em4QYTY/rcpt_M7i8hGac6av2gI7NmNXMVgmED4smaNN",
            "redaction": "null",
            "refunded": False,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": False,
                "url": "/v1/charges/ch_3LPSig2eZvKYlo2C1em4QYTY/refunds"
            },
            "review": "null",
            "shipping": "null",
            "source_transfer": "null",
            "statement_descriptor": "null",
            "statement_descriptor_suffix": "null",
            "status": "succeeded",
            "transfer_data": "null",
            "transfer_group": "null",
            "source": "tok_mastercard"
            }