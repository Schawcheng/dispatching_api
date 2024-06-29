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
from backstage import views

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('agents/', views.AgentsView.as_view()),
    path('agents/<int:agent_id>/', views.AgentDetailView.as_view()),
    path('recharges/', views.RechargesView.as_view()),
    path('recharges/<int:recharge_id>/', views.RechargeDetailView.as_view()),
    path('cards/', views.CardsView.as_view()),
    path('system-configs/', views.SystemConfigsView.as_view()),
    path('system-configs/<int:config_id>/', views.SystemConfigDetailView.as_view()),
    path('recharges-statistics/', views.RechargesStatisticsView.as_view()),
    path('recycle/', views.RecycleView.as_view()),
    path('cards-statistics/', views.CardsStatisticsView.as_view()),
    path('withdraw/', views.WithdrawView.as_view()),
    path('withdraw/<str:withdraw_no>/', views.WithdrawDetailView.as_view()),
]
