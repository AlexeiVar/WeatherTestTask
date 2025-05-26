from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views
schema_view = get_schema_view(
   openapi.Info(
      title="Weather statistics",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", views.index, name="weather"),
    path('statistics/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('statistics/counters/', views.GetCityCounters.as_view()),
    path('statistics/counters/<str:city>/', views.GetCityCounter.as_view()),
    path('statistics/history/', views.GetCheckedCities.as_view()),
    path('autocomplete', views.autocomplete, name='autocomplete')
]