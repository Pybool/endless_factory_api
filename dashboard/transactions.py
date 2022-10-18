import os, stripe
from dashboard.models import Refunds
from endless_factory_api.serializers import RefundSerializer
from dotenv import load_dotenv
load_dotenv()
stripe.api_key = str(os.getenv("STRIPE_SECRET_KEY"))

class InitiateTransaction(object):
    
    def __init__(self,cart,stripe_order_token):
        self.cart = cart
        self.stripe_order_token = stripe_order_token

    def create_charge(self):
        print(int(100*self.cart.grand_total()))
        return stripe.Charge.create(
                    amount = int(100*self.cart.grand_total()),
                    currency='usd',
                    description='Order payment for Goods bought on Endless Factory',
                    source = self.stripe_order_token
                )

class RefundTransactions(object):
    
    def __init__(self,charge_id,refund_id=''):
        
        self.charge_id = charge_id
        self.refund_id = refund_id
    
    def create_refund(self):
        response = stripe.Refund.create(charge=self.charge_id,)
        return response

    def retrieve_refund(self):
        response = stripe.Refund.retrieve(self.refund_id,)
        return response
    
    def update_refund(self,metadata):
        response = stripe.Refund.modify(self.refund_id,metadata=metadata,)
        return response
    
    def cancel_refund(self):
        response = stripe.Refund.cancel(self.refund_id,)
        return response
    
    def list_refunds(self,q,data_obj,singlecharge,limit,source="local_db"):
        if singlecharge:
            if source == "stripe":
                response = stripe.Refund.list(charge=self.charge_id,limit=limit)
                return response
            elif source == 'local_db':
                if type(int(q)) == int:
                    if data_obj == '':
                        refunds = Refunds.objects.filter(customer=q)
                        serializer = RefundSerializer(refunds,many=True)
                    else:
                        refunds = Refunds.objects.filter(customer=q,amount=data_obj.amount,currency=data_obj.currency,
                                                         status=data_obj.status,
                                                         created_at__range=[data_obj.start_date,data_obj.end_date]
                                                         )
                        serializer = RefundSerializer(refunds,many=True)
                return serializer.data
        else:
            if source == 'stripe':
                if q == '':
                    response = stripe.Refund.list(limit=limit)
                    return response
                
            if source == 'local_db':
                if q == '':
                        refunds = Refunds.objects.all()[:limit]
                        serializer = RefundSerializer(refunds,many=True)
                        return serializer.data
            