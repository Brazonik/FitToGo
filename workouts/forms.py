from django import forms
from .models import Workout, WorkoutRating
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['title', 'description', 'difficulty', 'muscle_group', 
                  'duration', 'calories', 'equipment_needed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = WorkoutRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} stars") for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What did you think of this workout?'})
        }

@login_required
def rate_workout(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    
    if request.user == workout.author:
        messages.warning(request, "You can't rate your own workout!")
        return redirect('workouts-detail', pk=pk)
    
    rating = WorkoutRating.objects.filter(user=request.user, workout=workout).first()
    
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.user = request.user
            new_rating.workout = workout
            new_rating.save()
            messages.success(request, 'Your rating has been saved!')
            return redirect('workouts-detail', pk=pk)
    else:
        form = RatingForm(instance=rating)
    
    return render(request, 'workouts/rate_workout.html', {
        'form': form,
        'workout': workout
    })