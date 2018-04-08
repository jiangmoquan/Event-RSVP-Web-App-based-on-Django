from django.urls import path
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    # path('', views.home),
    path('', login, {'template_name':'login/login.html'}),
    path('logout/', logout, {'template_name':'login/logout.html'}),
    path('register/',views.register,name='register'),






    path('profile/', views.profile, name='profile'),

    path('change-password/', views.change_password,name='change_password'),






]
