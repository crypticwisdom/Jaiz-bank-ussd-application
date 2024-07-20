from django.urls import path
from . import views, utils, cron


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('fund_reversal/', cron.fund_reversal, name='home'),
    path('update-category/', views.UpdateBillCategory.as_view()),
    path('update-package/', views.UpdatePackage.as_view()),
    path("endpoints/", views.EndPoints.as_view()),
    path('update-items/', views.UpdateItem.as_view()),
]


