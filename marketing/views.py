import logging

from decorators import allowed_users
log = logging.getLogger(__name__)
from collections import namedtuple
import json
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from endless_admin.translations import get_translations
from endless_factory_api.serializers import CampaignSerializer, PromoSerializer
from helpers import Datetimeutils
from marketing.models import Campaign

################MARKETING AND CAMPAIGNS####################

class NewCampaignView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def post(self,request):
        
        instance = CampaignSerializer(data=request.data)
        listings,variants,listings_variant = instance.get_listings_Object(request.data)
        request.data['listings'] = listings
        request.data['variants'] = variants
        request.data['listings_variants'] = listings_variant
        data = request.data
        instance = CampaignSerializer(data=data)
        if instance.is_valid(raise_exception=True):
            campaign = instance.create(data)
            print(dir(campaign))
            return Response({
                            "status":True,
                            "message":"Marketing campaign created successfully",
                            "data":{
                                    "campaign_name":campaign.campaign_name,
                                    "start_date":campaign.start_date,
                                    "end_date":campaign.end_date
                                    }
                                })
    def get(self,request):
        
        promotions = Campaign.objects.filter(is_active=False)
        # print(promotions)
        # for promotion in promotions:
        #     print(type(promotion))
        #     listings = promotion.listings.all()
        #     variants = promotion.variants.all()
        #     listings_serializer = ProductSerializer(listings,many=True)
        #     variants_serializer = VariantSerializer(variants,many=True)
        #     # print(listings_serializer.data)
        #     # print("\n\n\n")
        #     # print(variants_serializer.data)
        #     # promotion.listings = listings
        #     promotion.listings.set(listings)
        #     print(PromoSerializer(promotions,many=False).data)
        serializer = PromoSerializer(promotions,many=True)
        
        print(serializer.data)
        return Response({"status":True,"data":serializer.data})
            
                     