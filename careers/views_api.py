from itertools import product
import json
import logging
from endless_factory_api.paginationclasses import HeaderLimitOffsetPagination
log = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from endless_factory_api.serializers import *
from datetime import datetime, timezone
from django.db.models import Q 
from careers.models import *
from rest_framework.pagination import LimitOffsetPagination
from endless_factory_api.custompagination import CustomPaginatorClass

class CareerJobsViewAll(APIView):
    
    def get(self,request):
        jobs = Job.objects.all()
        serializer= JobSerializer(jobs, many=True)
        return Response({"jobs":serializer.data,"message":"Jobs fetched successfully","status":True})
    

class SubmitJobApplicationView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def post(self,request):
        
        with transaction.atomic():
            docs = ['resume-documents']
            if request.method == 'POST':
                try:
                    data = request.data['data']
                except Exception as e:
                    return Response({'errors': str(e), "status": False})
            
                try:
                    data = json.loads(data)
                except:
                    return Response({'errors': serializer.errors,'message':'Invalid json format supplied', "status": False})
                
                applied = Applications.objects.filter(job=Job.objects.get(slug=data['slug']), applicant= Applicant.objects.get_or_create(user=request.user)[0].id)
                print("Has Applied "+str(applied))
                if len(applied) > 0:
                    return Response({"status": False,'message':"You have previously applied for this job or this job is now unavailable"})
                request.data['user'] = request.user.id
                try:
                    data['job'] = Job.objects.get(slug=data['slug']).id
                    data['company'] = Company.objects.get(id=int(data['company'])).id
                    data['applicant'] = Applicant.objects.get_or_create(user=request.user)[0].id
                    serializer= ApplicationSerializer(data=data)
                    print(data)
                except Exception as e:
                    return Response({'errors': str(e),'message':'Something went wrong while submitting your application', "status": False})
                if serializer.is_valid():
                    instance = serializer.save()
                    for doc in docs:
                        instance = self.saveAttachments(request,instance,data,request.FILES.getlist(doc, None),doc)
                    if instance:
                        instance.save()
                        return Response({"status": True,'message':"Your application for this role was successfully submitted",'data': serializer.data})
                    else:
                        return Response({'errors': serializer.errors, "status": 'error'})
                else:
                    return Response({'errors': serializer.errors, "status": 'error'})
    
    
    def saveAttachments(self,request,instance,data,files,doc=''):
        
        if request.method == 'POST':
            print("Files ",files,doc)
            data['user'] = request.user
            if doc == 'resume-documents':
                instance = ApplicationResumeSerializer(data=data,context={'resume-documents': files})
            if instance.is_valid():
                return instance.create(data)
