

from django.urls import path

from . import views


urlpatterns = [
    path('', views.ContainerList.as_view()),
    path('<int:pk>/', views.ContainerRecord.as_view()),

    path('<int:containerid>/features/', views.Features.as_view()),

    path('<int:containerid>/documents/', views.Documents.as_view()),

    # path('<int:containerid>/features/', views.FeaturesList.as_view()),

    # path('<int:containerid>/features/<int:feats>/<int:featsperdoc>/<int:docsperfeat>/',
    #      views.FeaturesRecord.as_view()),
    #
    # path('<int:containerid>/get-features/<int:feats>/<int:featsperdoc>/<int:docsperfeat>/',
    #      views.get_features),

    path('test-celery/<int:a>/<int:b>', views.test_celery),

    # todo(): delete these (4 urls that follow):
    # path('url/', views_neo.Urls.as_view()),
    # path('url/<int:pk>/', views_neo.UrlRecord.as_view()),
    #
    # path('crawl-status/', views_neo.CrawlStatus.as_view()),
    # path('crawl-status/<int:pk>/', views_neo.CrawlStatusRecord.as_view()),

]
