from .models import *
from rest_framework import serializers


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        exclude = []


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = []


# class ProvideSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Provider
#         exclude = []
#         depth = 1


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        exclude = []


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = []
        depth = 1


class AirtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airtime
        exclude = []
        depth = 1


class FundTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransfer
        exclude = []
        depth = 1


class ElectricitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Electricity
        exclude = []
        depth = 1


class CableSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CableSubscription
        exclude = []
        depth = 1




