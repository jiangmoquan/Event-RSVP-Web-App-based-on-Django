from django.urls import path
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    path('', views.index, name='index'),

    # path('profile/edit/', views.edit_profile, name='edit_profile'),
    # path('profile/create-event/', views.create_event, name='create_event'),
    # path('profile/create-event/invite-guest/', views.invite_guest, name='invite_guest'),

    path('add/', views.addevent, name='add'),
    path('edit/<int:naire_id>/', views.edit, name='edit'),
    path('invite/<int:event_id>/', views.invite, name = 'invite'),
    path('view-response/<int:naire_id>/',views.view_response, name='view-response'),
    path('reply/<int:naire_id>/', views.reply, name='response'),
    path('finalize/<int:naire_id>/', views.finalize, name='finalize'),

    # url(r'^del_question/(\d+)/$', views.del_question, name='del_que'),
    # url(r'^delete/$', views.delete, name='delete'),
    # url(r'^show/(\d+)/(\d+)/$', views.show, name='show'),

]