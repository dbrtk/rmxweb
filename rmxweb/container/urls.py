

from django.urls import path

from . import views


urlpatterns = [

    path('', views.ContainerList.as_view()),
    path('<int:pk>/', views.ContainerRecord.as_view()),

]
