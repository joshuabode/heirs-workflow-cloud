"""tasks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from tasktable import views
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('', views.landing),
    path('see-approve-requests/', views.viewready),
    path('see-pre-approve-requests/', views.previewready),
    path('user/', include('django.contrib.auth.urls')),
    path('user/logout', views.logout_view),
    path('user/home', views.home),
    path('tasks/', include('tasktable.urls')),
    path('myprojects/', views.projects),
    path('admin/', admin.site.urls),
    path('projects/<int:id>/', views.projectdetails),
    path('projects/<int:id>/filespace', views.filespace),
    path('projects/<int:id>/edit', views.editproject),
    path('tasks/<int:id>/edit', views.edittask),
    path('download/<int:id>', views.download),
    path('newtask/', views.newtask),
    path('newproject/', views.newproject),
    path('newstatus/', views.newstatus),
    path('upload/', views.uploadfile),
    path('forgot-password/', views.forgot),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catalog'),
    path('dismiss/<int:notification_id>', views.dismiss_notification),
    path('dismiss-all', views.dismiss_all),

]

admin.site.site_header = "HWC Control Board"
admin.site.site_title = "HWC Control Board"
admin.site.index_title = "Welcome to the Control Board"
