from django.urls import path

from . import api_views


urlpatterns = [
    path('snake/levels/', api_views.snake_levels_api, name='snake_levels_api'),
    path('snake/levels/<int:level_id>/', api_views.snake_level_detail_api, name='snake_level_detail_api'),
    path('snake/result/', api_views.snake_result_api, name='snake_result_api'),
    path('snake/history/', api_views.snake_history_api, name='snake_history_api'),
]
