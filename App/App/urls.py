"""
URL configuration for App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework import routers

from API import views
from Frontend import views as frontend_views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'packets', views.PacketsViewSet)
router.register(r'agents', views.AgentsViewSet)
router.register(r'analysis', views.AnalysisViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', frontend_views.index, name="index"),
    path('home/',frontend_views.home, name="home"),
    path('agent/',frontend_views.agent, name="agent"),
    path('settings/',frontend_views.settings, name="settings"),
    path('signout/',frontend_views.signout, name="signout"),
    path('accounts/login/', frontend_views.index, name="index")
]