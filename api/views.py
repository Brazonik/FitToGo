from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from workouts.models import Workout, Exercise, WorkoutTag, WorkoutRating, SavedWorkout
from .serializers import (
    WorkoutSerializer, ExerciseSerializer, 
    WorkoutTagSerializer, WorkoutRatingSerializer, WorkoutExerciseSerializer
)

class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'author__username']
    ordering_fields = ['created_at', 'avg_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Workout.objects.all()
        
        queryset = queryset.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        )
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        muscle_group = self.request.query_params.get('muscle_group')
        if muscle_group:
            queryset = queryset.filter(muscle_group=muscle_group)
            
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        workout = self.get_object()
        if request.user.is_authenticated:
            _, created = SavedWorkout.objects.get_or_create(
                user=request.user,
                workout=workout
            )
            return Response({'saved': True, 'created': created})
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['post'])
    def unsave(self, request, pk=None):
        workout = self.get_object()
        if request.user.is_authenticated:
            deleted, _ = SavedWorkout.objects.filter(
                user=request.user,
                workout=workout
            ).delete()
            return Response({'unsaved': True, 'deleted': deleted > 0})
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'muscle_targeted']

class WorkoutTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkoutTag.objects.all()
    serializer_class = WorkoutTagSerializer

class WorkoutChoicesView(APIView):
    def get(self, request):
        return Response({
            'difficulty_choices': Workout.DIFFICULTY_CHOICES,
            'muscle_group_choices': Workout.MUSCLE_GROUP_CHOICES
        })
