from django.urls import path
from . import views


urlpatterns = {
    path('test_db', views.test_db, name='test_db'),
    path('construct_db', views.construct_db, name='construct_db')
}