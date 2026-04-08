from django.urls import path
from . import views

urlpatterns = [
    path('', views.games_home, name='games_home'),
    path('menu-builder/levels/', views.menu_builder_levels, name='menu_builder_levels'),
    path('menu-builder/game/<int:level_id>/', views.menu_builder_game, name='menu_builder_game'),
    path('calorie-counter/levels/', views.calorie_counter_levels, name='calorie_counter_levels'),
    path('calorie-counter/game/<str:difficulty>/', views.calorie_counter_game, name='calorie_counter_game'),
    path('calorie-counter/game/', views.calorie_counter_game, name='calorie_counter_game_default'),
    path('statistics/', views.user_statistics, name='user_statistics'),
]
