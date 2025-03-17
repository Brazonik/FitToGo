from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Workout(models.Model):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    
    DIFFICULTY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]
    
    FULL_BODY = 'Full Body'
    UPPER_BODY = 'Upper Body'
    LOWER_BODY = 'Lower Body'
    CORE = 'Core'
    ARMS = 'Arms'
    CHEST = 'Chest'
    BACK = 'Back'
    LEGS = 'Legs'
    SHOULDERS = 'Shoulders'
    CARDIO = 'Cardio'
    
    MUSCLE_GROUP_CHOICES = [
        (FULL_BODY, 'Full Body'),
        (UPPER_BODY, 'Upper Body'),
        (LOWER_BODY, 'Lower Body'),
        (CORE, 'Core'),
        (ARMS, 'Arms'),
        (CHEST, 'Chest'),
        (BACK, 'Back'),
        (LEGS, 'Legs'),
        (SHOULDERS, 'Shoulders'),
        (CARDIO, 'Cardio'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField(help_text="Describe the workout in detail including sets, reps, and form instructions.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    difficulty = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_CHOICES,
        default=INTERMEDIATE
    )
    muscle_group = models.CharField(
        max_length=20,
        choices=MUSCLE_GROUP_CHOICES,
        default=FULL_BODY
    )
    
    duration = models.PositiveIntegerField(
        help_text="Estimated duration in minutes",
        null=True, blank=True
    )
    calories = models.PositiveIntegerField(
        help_text="Estimated calories burned",
        null=True, blank=True
    )
    equipment_needed = models.CharField(
        max_length=200,
        help_text="List any equipment needed, separated by commas",
        blank=True
    )
    tags = models.ManyToManyField('WorkoutTag', blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('workouts-detail', kwargs={'pk': self.pk})

class SavedWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'workout')
        
    def __str__(self):
        return f"{self.user.username} saved {self.workout.title}"

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    equipment = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, related_name='exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, default="10-12")
    rest_time = models.CharField(max_length=50, default="60 seconds")
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets} sets x {self.reps}"

class WorkoutTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class WorkoutRating(models.Model):
    workout = models.ForeignKey(Workout, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('workout', 'user')
    
    def __str__(self):
        return f"{self.user.username}: {self.rating}/5 for {self.workout.title}"

