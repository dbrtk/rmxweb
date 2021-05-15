

from django.urls import path

from . import views


urlpatterns = [
    path('', views.ListData.as_view()),
    path('<int:pk>/', views.DataRecord.as_view()),
]
