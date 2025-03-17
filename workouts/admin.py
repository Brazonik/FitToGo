from django.contrib import admin
from . import models

class WorkoutExerciseInline(admin.TabularInline):
    model = models.WorkoutExercise
    extra = 1

class WorkoutAdmin(admin.ModelAdmin):
    inlines = [WorkoutExerciseInline]
    list_display = ('title', 'author', 'difficulty', 'muscle_group', 'created_at')
    list_filter = ('difficulty', 'muscle_group', 'author')
    search_fields = ('title', 'description')

# Register your models here.
admin.site.register(models.Workout, WorkoutAdmin)
admin.site.register(models.SavedWorkout)
admin.site.register(models.Exercise)
admin.site.register(models.WorkoutExercise)