from django.urls import path
from . import views

urlpatterns = [
    path('', views.idea_list, name='idea_list'),
    path('idea/create/', views.idea_create, name='idea_create'),
    path('idea/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    path('idea/<int:idea_id>/update/', views.idea_update, name='idea_update'),
    path('idea/<int:idea_id>/delete/', views.idea_delete, name='idea_delete'),
    
    path('idea/<int:idea_id>/toggle-star/', views.idea_toggle_star, name='idea_toggle_star'),
    path('idea/<int:idea_id>/change-interest/', views.idea_change_interest, name='idea_change_interest'),
    
    path('devtool/', views.devtool_list, name='devtool_list'),
    path('devtool/create/', views.devtool_create, name='devtool_create'),
    path('devtool/<int:devtool_id>/', views.devtool_detail, name='devtool_detail'),
    path('devtool/<int:devtool_id>/update/', views.devtool_update, name='devtool_update'),
    path('devtool/<int:devtool_id>/delete/', views.devtool_delete, name='devtool_delete'),
]