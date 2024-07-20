from django.shortcuts import render
from home import models
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from management_api import management_serializer

# Create your views here.


class SessionView(APIView):
    permission_classes = []

    def get(self, request):
        query_set = models.Session.objects.all().order_by("id")

        if query_set is not None:
            serializer = management_serializer.SessionSerializer(query_set, many=True)
            return Response({"message": serializer.data, "response_status": True}, status=HTTP_200_OK)
        return Response({"message": "No sessions", "response_status": False}, status=HTTP_400_BAD_REQUEST)


class CustomerView(APIView):
    permission_classes = []

    def get(self, request):
        query_set = models.Customer.objects.all().order_by("id")
        if query_set is not None:
            serializer = management_serializer.CustomerSerializer(query_set, many=True)
            return Response({"message": serializer.data, "response_status": True}, status=HTTP_200_OK)
        return Response({"message": "No customers", "response_status": False}, status=HTTP_400_BAD_REQUEST)


class DataView(APIView):
    permission_classes = []

    def get(self, request):
        query_set = models.Data.objects.all().order_by("id")
        if query_set is not None:
            serializer = management_serializer.DataSerializer(query_set, many=True)
            return Response({"message": serializer.data, "response_status": True}, status=HTTP_200_OK)
        return Response({"message": "No Data purchase", "response_status": False}, status=HTTP_400_BAD_REQUEST)


class FundTransferView(APIView):
    permission_classes = []

    def get(self, request):
        query_set = models.FundTransfer.objects.all().order_by("id")
        if query_set is not None:
            serializer = management_serializer.FundTransferSerializer(query_set, many=True)
            return Response({"message": serializer.data, "response_status": True}, status=HTTP_200_OK)
        return Response({"message": "No Fund Transaction", "response_status": False}, status=HTTP_400_BAD_REQUEST)


class ElectricityView(APIView):
    permission_classes = []

    def get(self, request):
        query_set = models.Electricity.objects.all().order_by("id")
        if query_set is not None:
            serializer = management_serializer.ElectricitySerializer(query_set, many=True)
            return Response({"message": serializer.data, "response_status": True}, status=HTTP_200_OK)
        return Response({"message": "No Electricity Purchase", "response_status": False},
                        status=HTTP_400_BAD_REQUEST)


