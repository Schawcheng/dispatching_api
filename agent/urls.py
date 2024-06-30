"""
URL configuration for dispatching_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from agent import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('subordinates/', views.SubordinatesView.as_view()),
    path('recharges/', views.RechargesView.as_view()),
    path('recharges/<str:recharge_no>/', views.RechargeDetailView.as_view()),
    path('withdraws/', views.WithdrawsView.as_view()),
    path('cards/', views.CardsView.as_view()),
    path('payments/', views.PaymentTypesView.as_view()),
    path('payments/update/', views.PaymentTypeDetailView.as_view()),
    path('banks/', views.BanksView.as_view()),
    path('subordinates-statistics/', views.SubordinatesStatisticsView.as_view()),
    path('my-info/', views.MyInfoView.as_view()),
    path('support/', views.SupportDetailView.as_view()),
    path('my-points/', views.MyPointsView.as_view()),
    path('my-cards-statistics/', views.MyCardsStatistic.as_view()),
    path('team-total-transaction-statistics/', views.TotalTransactionsStatisticsView.as_view())
]
