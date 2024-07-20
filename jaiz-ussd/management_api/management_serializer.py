from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from home import models


class SessionSerializer(ModelSerializer):

    class Meta:
        model = models.Session
        fields = "__all__"


class CustomerSerializer(ModelSerializer):

    class Meta:
        model = models.Customer
        fields = "__all__"


class DataSerializer(ModelSerializer):
    class Meta:
        model = models.Data
        fields = "__all__"


class FundTransferSerializer(ModelSerializer):
    class Meta:
        model = models.FundTransfer
        fields = "__all__"


class ElectricitySerializer(ModelSerializer):
    class Meta:
        model = models.Electricity
        fields = "__all__"

