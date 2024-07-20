from django.urls import path
from management_api.views import SessionView, CustomerView, DataView, FundTransferView, ElectricityView
# from views import

urlpatterns = [
    path("user-sessions/", SessionView.as_view(), name="user-sessions"),
    path("customers/", CustomerView.as_view(), name="customers"),
    path("data-purchase/", DataView.as_view(), name="data-purchase"),
    path("fund-transfers/", FundTransferView.as_view(), name="fund-transfers"),
    path("electricity-purchase/", ElectricityView.as_view(), name="electricity-purchase")
]
