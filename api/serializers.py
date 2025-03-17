from rest_framework import serializers
from workouts.models import Workout, WorkoutTag, WorkoutRating, Exercise, WorkoutExercise, SavedWorkout
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class WorkoutTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutTag
        fields = ['id', 'name']

class WorkoutRatingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = WorkoutRating
        fields = ['id', 'rating', 'review', 'created_at', 'user', 'username']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'muscle_targeted', 'description', 'instructions', 'equipment']

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()
    
    class Meta:
        model = WorkoutExercise
        fields = ['id', 'exercise', 'sets', 'reps', 'rest_time', 'order']

class WorkoutSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    tags = WorkoutTagSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True, required=False)
    rating_count = serializers.IntegerField(read_only=True, required=False)
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Workout
        fields = [
            'id', 'title', 'description', 'difficulty', 'muscle_group', 
            'duration', 'calories', 'equipment_needed', 'created_at',
            'author', 'author_username', 'tags', 'avg_rating', 'rating_count',
            'is_saved'
        ]
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedWorkout.objects.filter(user=request.user, workout=obj).exists()
        return False