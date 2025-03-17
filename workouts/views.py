from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Workout, SavedWorkout, Exercise, WorkoutExercise, WorkoutRating, WorkoutTag
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django import forms
from django.db.models import Avg, Count, Q
from .forms import WorkoutForm, RatingForm
from django.views.decorators.http import require_POST

class WorkoutListView(ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'
    context_object_name = 'object_list'
    paginate_by = 10
    
    def get_queryset(self):
        difficulty = self.request.GET.get('difficulty', '')
        muscle_group = self.request.GET.get('muscle_group', '')
        query = self.request.GET.get('q', '')
        
        queryset = Workout.objects.all().order_by('-created_at')
        
        queryset = queryset.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        )
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if muscle_group:
            queryset = queryset.filter(muscle_group=muscle_group)
            
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains(query)) |
                Q(author__username__icontains(query))
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['difficulty_choices'] = Workout.DIFFICULTY_CHOICES
        context['muscle_group_choices'] = Workout.MUSCLE_GROUP_CHOICES
        
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_muscle_group'] = self.request.GET.get('muscle_group', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        context['filtered'] = any([
            context['selected_difficulty'],
            context['selected_muscle_group'],
            context['search_query']
        ])
        
        return context

class WorkoutDetailView(DetailView):
    model = Workout
    template_name = 'workouts/workout_detail.html'  
    context_object_name = 'workout'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout = self.get_object()
        
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedWorkout.objects.filter(
                user=self.request.user, 
                workout=workout
            ).exists()
            
            context['user_rating'] = WorkoutRating.objects.filter(
                user=self.request.user,
                workout=workout
            ).first()
        
        ratings = WorkoutRating.objects.filter(workout=workout)
        context['workout_ratings'] = ratings
        
        avg = ratings.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = avg if avg else 0
        
        return context

class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class WorkoutUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        
    def test_func(self):
        workout = self.get_object()
        return self.request.user == workout.author

class WorkoutDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Workout
    success_url = '/'
    
    def test_func(self):
        workout = self.get_object()
        return self.request.user == workout.author
    
    def delete(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True})
        else:
            return super().delete(request, *args, **kwargs)

class AddExerciseForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.all())
    
    class Meta:
        model = WorkoutExercise
        fields = ['exercise', 'sets', 'reps', 'rest_time', 'order']

class AddExerciseView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = WorkoutExercise
    form_class = AddExerciseForm
    template_name = 'workouts/add_exercise.html'
    
    def form_valid(self, form):
        workout_id = self.kwargs.get('pk')
        workout = get_object_or_404(Workout, pk=workout_id)
        form.instance.workout = workout
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('workouts-detail', kwargs={'pk': self.kwargs.get('pk')})
    
    def test_func(self):
        workout_id = self.kwargs.get('pk')
        workout = get_object_or_404(Workout, pk=workout_id)
        return self.request.user == workout.author

class RateWorkoutForm(forms.ModelForm):
    class Meta:
        model = WorkoutRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} stars") for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this workout...'})
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

@login_required
def save_workout(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    
    if SavedWorkout.objects.filter(user=request.user, workout=workout).exists():
        messages.info(request, f"You've already saved '{workout.title}'")
    else:
        SavedWorkout.objects.create(user=request.user, workout=workout)
        messages.success(request, f"You've saved '{workout.title}'")
    
    return redirect('workouts-detail', pk=pk)

@login_required
def unsave_workout(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    saved = SavedWorkout.objects.filter(user=request.user, workout=workout)
    
    if saved.exists():
        saved.delete()
        messages.success(request, f"You've unsaved '{workout.title}'")
    else:
        messages.info(request, f"You hadn't saved '{workout.title}'")
    
    return redirect('workouts-detail', pk=pk)

def about(request):
    return render(request, 'workouts/about.html', {'title': 'About'})

class WorkoutTagListView(ListView):
    model = WorkoutTag
    template_name = 'workouts/tag_list.html'
    context_object_name = 'tags'
    ordering = ['name']

class WorkoutsByTagListView(ListView):
    model = Workout
    template_name = 'workouts/workouts_by_tag.html'
    context_object_name = 'workouts'
    
    def get_queryset(self):
        tag = get_object_or_404(WorkoutTag, name=self.kwargs.get('tag_name'))
        return tag.workout_set.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.kwargs.get('tag_name')
        return context

def workout_list_alpine(request):
    """View to serve the Alpine.js enhanced workout list"""
    context = {
        'difficulty_choices': Workout.DIFFICULTY_CHOICES,
        'muscle_group_choices': Workout.MUSCLE_GROUP_CHOICES,
        'selected_difficulty': request.GET.get('difficulty', ''),
        'selected_muscle_group': request.GET.get('muscle_group', ''),
        'search_query': request.GET.get('q', '')
    }
    return render(request, 'workouts/workout_list_alpine.html', context)

def workout_list_api(request):
    """API endpoint for fetching workouts"""
    difficulty = request.GET.get('difficulty', '')
    muscle_group = request.GET.get('muscle_group', '')
    
    queryset = Workout.objects.all()
    
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    if muscle_group:
        queryset = queryset.filter(muscle_group=muscle_group)
    
    workouts = list(queryset.values(
        'id', 'title', 'description', 'difficulty', 'muscle_group',
        'created_at', 'author__username'
    ))
    
    for workout in workouts:
        workout['author_username'] = workout.pop('author__username')
    
    return JsonResponse(workouts, safe=False)

def choices_api(request):
    """API endpoint for fetching choice fields"""
    return JsonResponse({
        'difficulty_choices': list(Workout.DIFFICULTY_CHOICES),
        'muscle_group_choices': list(Workout.MUSCLE_GROUP_CHOICES)
    })

from django.shortcuts import render, get_object_or_404
from .models import Workout

def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    return render(request, 'workouts/workout_detail.html', {'workout': workout})

@login_required
def workout_ratings_api(request, pk):
    """API endpoint to get workout ratings"""
    try:
        workout = Workout.objects.get(pk=pk)
        ratings = WorkoutRating.objects.filter(workout=workout)
        
        ratings_data = []
        for rating in ratings:
            ratings_data.append({
                'id': rating.id,
                'username': rating.user.username,
                'rating': rating.rating,
                'review': rating.review,
                'created_at': rating.created_at.strftime('%Y-%m-%d')
            })
        
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        return JsonResponse({
            'ratings': ratings_data,
            'average_rating': avg_rating,
            'count': ratings.count()
        })
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)

@login_required
@require_POST
def save_workout_api(request, pk):
    """API endpoint to save a workout"""
    try:
        workout = Workout.objects.get(pk=pk)
        saved, created = SavedWorkout.objects.get_or_create(user=request.user, workout=workout)
        return JsonResponse({'success': True})
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)

@login_required
@require_POST
def unsave_workout_api(request, pk):
    """API endpoint to unsave a workout"""
    try:
        SavedWorkout.objects.filter(user=request.user, workout_id=pk).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def rate_workout_api(request, pk):
    """API endpoint to rate a workout"""
    try:
        workout = Workout.objects.get(pk=pk)
        
        if workout.author == request.user:
            return JsonResponse({'error': 'You cannot rate your own workout'}, status=400)
        
        rating_value = int(request.POST.get('rating', 0))
        if not 1 <= rating_value <= 5:
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
            
        review = request.POST.get('review', '')
        
        rating, created = WorkoutRating.objects.update_or_create(
            user=request.user,
            workout=workout,
            defaults={'rating': rating_value, 'review': review}
        )
        
        return JsonResponse({'success': True})
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)