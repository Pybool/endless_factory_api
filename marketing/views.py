import logging
from accounts.models import User
import random
from itertools import chain
from decorators import allowed_users
log = logging.getLogger(__name__)
from collections import namedtuple
import json
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from endless_admin.translations import get_translations
from endless_factory_api.serializers import CampaignSerializer, AdsSerializer
from helpers import Datetimeutils
from marketing.models import Campaign

################MARKETING AND CAMPAIGNS####################

class NewCampaignView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
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
        user = request.GET.get('uid','')
     
        promotions = Campaign.objects.filter(user=get_object_or_404(User,pk=int(user))) if isinstance(int(user),int) else None
        
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
        serializer = AdsSerializer(promotions,many=True)
        
        print(serializer.data)
        return Response({"status":True,"data":serializer.data})
            

class CampaignActionsView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        
        ad = int(request.GET.get('id'))
        action = request.GET.get('action')
        assert(action == 'resume' or action== 'pause' or action=='end' or action=='delete')
        if action != 'end' and action !='delete':
            action_flag = True if action == 'resume' else False
            Campaign.objects.filter(id=ad).update(is_active=action_flag,schedule_cmd='user')
            ad = Campaign.objects.filter(id=ad).values()
            return Response({"status":True,"data":ad})
        
        if action == 'end':
            instance = Campaign.objects.filter(id=ad).update(is_schedule=False,schedule_cmd='user')
            return Response({"status":True,"data":f"Operation was successful"})
        
        if action == 'delete':
            instance = Campaign.objects.filter(id=ad).delete()
            return Response({"status":True,"data":f"Operation was successful"})
        

class CampaignFeederView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        ads_count = Campaign.objects.filter().count()
        ids = Campaign.objects.filter().values_list('id')

        flatten_ids = list(chain.from_iterable(ids))
        if ads_count < 1:
            return Response({"status":False,"message":"There are no active ads to display"})  
        try:
            
            random_ads_ids = random.sample(range(max(flatten_ids)+1), min(flatten_ids)) if ads_count < 11 else random.sample(range(max(flatten_ids)+1), 10)
            if 0 in random_ads_ids:
                random_ads_ids.remove(0)
            random_ads = Campaign.objects.filter(id__in=random_ads_ids, is_active=True,is_schedule=True).values()
            return Response({"status":True,"ads":random_ads})    
        except Exception as e: 
            return Response({"status":str(e)})  


class CampaignAdsClick(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        id = request.GET.get('id')
        try:
            click_count = Campaign.objects.filter(id=id).values('clicks').first()
            if Campaign.objects.filter(id=id).values('clicks').update(clicks = click_count['clicks'] + 1):
                return Response({"status":True,"message":"Click count incremented for the ad"})   
        except Exception as e:
            log.info(str("An error occured while incrementing add count, this campaign may be inactive or deleted")+str(e))
            return Response({"status":False,"message":"An error occured while incrementing add count, this campaign may be inactive or deleted"})
        
        
        
        
        
