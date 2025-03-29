from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', user_login, name='login'),
    path('', questions_list, name='home'),  # Root URL named 'home'
    path('submit_answer/', submit_answer, name='submit_answer'),
    path('logout/', user_logout, name='logout'),
    path('export-answers/', export_answers_to_excel, name='export_answers'),
    path('admin-panel/', admin_panel, name='admin_panel'),  # Admin panel URL
    path('export-user-answers/<int:user_id>/', export_user_answers, name='export_user_answers'),
]