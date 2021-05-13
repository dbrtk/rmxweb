

from django.urls import path

from . import views


urlpatterns = [

    path('', views.Graph.as_view()),
    path('dendogram/', views.Dendogram.as_view()),

    path('context/', views.get_context),
    path('features/', views.list_features),
]
