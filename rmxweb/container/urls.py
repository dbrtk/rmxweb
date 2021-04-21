

from django.urls import path

from . import views

urlpatterns = [
    path('', views.ContainerList.as_view()),
    path('<int:pk>/', views.ContainerRecord.as_view()),

    path('test-celery/<int:a>/<int:b>', views.test_celery),

    # todo(): delete these (4 urls that follow):
    # path('url/', views.Urls.as_view()),
    # path('url/<int:pk>/', views.UrlRecord.as_view()),
    #
    # path('crawl-status/', views.CrawlStatus.as_view()),
    # path('crawl-status/<int:pk>/', views.CrawlStatusRecord.as_view()),

]
