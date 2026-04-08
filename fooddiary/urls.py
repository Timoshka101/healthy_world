from django.urls import path
from . import views

app_name = 'fooddiary'

urlpatterns = [
    path('', views.fooddiary_home, name='fooddiary_home'),
    path('search/', views.search_foods, name='search_foods'),
    path('add/', views.add_food_to_diary, name='add_food_to_diary'),
    path('create_food/', views.create_food, name='create_food'),
    path('settings/', views.user_settings, name='user_settings'),
    path('delete_entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]