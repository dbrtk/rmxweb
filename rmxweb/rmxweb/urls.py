"""rmxweb URL Configuration

The `urlpatterns` list routes URLs to views_neo. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views_neo
    1. Add an import:  from my_app import views_neo
    2. Add a URL to urlpatterns:  path('', views_neo.home, name='home')
Class-based views_neo
    1. Add an import:  from other_app.views_neo import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from home import views as home_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home_views.home),

    path('container/', include('container.urls')),
    path('data/', include('data.urls')),

    path('graph/', include('graph.urls')),
    path('feature/', include('feature.urls')),
]
