from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path('', views.review_list, name='review_list'),  
    path('<int:pk>/', views.review_detail, name='detail'),  
    path('create/', views.review_create, name='create'),  
    path('<int:pk>/update/', views.review_update, name='update'),  
    path('<int:pk>/delete/', views.review_delete, name='delete'), 
]