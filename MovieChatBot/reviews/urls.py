from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path('', views.review_list, name='review_list'),  
    path('search/', views.search, name='search'),
    path('<int:pk>/', views.review_detail, name='detail'),  
    path('create/', views.review_create, name='create'),  
    path('<int:pk>/update/', views.review_update, name='update'),  
    path('<int:pk>/delete/', views.review_delete, name='delete'), 

    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('<int:pk>/comments/create/', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    path('<int:pk>/like/', views.like_toggle, name='like_toggle'),
    
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('api/ping', views.ping, name='ping'),
    path('api/chatbot', views.chatbot, name='chatbot'),
]