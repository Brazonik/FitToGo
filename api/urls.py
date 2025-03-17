from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'workouts', views.WorkoutViewSet, basename='workout')
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'tags', views.WorkoutTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('choices/', views.WorkoutChoicesView.as_view(), name='choices'),
]