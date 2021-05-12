

from django.urls import path

from . import views


urlpatterns = [

    path('', views.Graph.as_view()),
    # path('hierarchical/', views.Hierarchical.as_view()),
    # path('kmeans/', views.Kmeans.as_view()),
]
