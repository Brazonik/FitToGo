from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.WorkoutListView.as_view(), name="workouts-home"),
    path('workout/<int:pk>/', views.WorkoutDetailView.as_view(), name="workouts-detail"),
    path('workout/create', views.WorkoutCreateView.as_view(), name="workouts-create"),
    path('workout/<int:pk>/update', views.WorkoutUpdateView.as_view(), name="workouts-update"),
    path('workout/<int:pk>/delete', views.WorkoutDeleteView.as_view(), name="workouts-delete"),
    path('workout/<int:pk>/save/', views.save_workout, name='workouts-save'),
    path('workout/<int:pk>/unsave/', views.unsave_workout, name='workouts-unsave'),
    path('workout/<int:pk>/add-exercise/', views.AddExerciseView.as_view(), name='workouts-add-exercise'),
    path('workout/<int:pk>/rate/', views.rate_workout, name='workouts-rate'),
    path('tags/', views.WorkoutTagListView.as_view(), name='workouts-tags'),
    path('tags/<str:tag_name>/', views.WorkoutsByTagListView.as_view(), name='workouts-by-tag'),
    path('about/', views.about, name="workouts-about"),
    path('workouts/alpine/', views.workout_list_alpine, name='workout-list-alpine'),
    path('alpine/', views.workout_list_alpine, name='workout-list-alpine'),    
    path('api/workouts/', views.workout_list_api, name='workout-list-api'),
    path('api/choices/', views.choices_api, name='choices-api'),
    path('workouts/<int:pk>/', RedirectView.as_view(pattern_name='workouts-detail')),
]

urlpatterns += [
    path('api/workout/<int:pk>/ratings/', views.workout_ratings_api, name='workout-ratings-api'),
    path('api/workout/<int:pk>/save/', views.save_workout_api, name='workout-save-api'),
    path('api/workout/<int:pk>/unsave/', views.unsave_workout_api, name='workout-unsave-api'),
    path('api/workout/<int:pk>/rate/', views.rate_workout_api, name='workout-rate-api'),
]