from django.urls import path

from . import views

urlpatterns = [
    path('', views.mytasks, name='tasks'),
    path('<int:id>/', views.details, name='details'),
    path('<int:id>/status', views.status, name='status'),
    path('<int:id>/approve', views.approve, name='approve'),
    path('<int:id>/pre-approve', views.pre_approve, name='pre-approve'),
    path('<int:id>/references', views.download),
    path('manage', views.index, name='manage'),
    path('<int:id>/delete', views.delete_task)
]
