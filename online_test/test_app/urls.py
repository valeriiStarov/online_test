from django.urls import path
from .views import *


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('test_group/<int:test_group_pk>', TestGroupView.as_view(), name='test_group'),
    path('test/<int:test_pk>', TestView.as_view(), name='test'),
    path('statistics/<int:stat_pk>', TestStatisticsView.as_view(), name='statistics'),
    path('statistics/test_group/<int:test_group_pk>', TestGroupStatistics.as_view(), name='test_group_statistics')
]