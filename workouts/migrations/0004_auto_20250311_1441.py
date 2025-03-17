# Generated by Django 3.2.13 on 2025-03-11 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0003_auto_20250310_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='description',
            field=models.TextField(help_text='Describe the workout in detail including sets, reps, and form instructions.'),
        ),
        migrations.AlterField(
            model_name='workout',
            name='difficulty',
            field=models.CharField(choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], default='Intermediate', max_length=20),
        ),
        migrations.AlterField(
            model_name='workout',
            name='muscle_group',
            field=models.CharField(choices=[('Full Body', 'Full Body'), ('Upper Body', 'Upper Body'), ('Lower Body', 'Lower Body'), ('Core', 'Core'), ('Arms', 'Arms'), ('Chest', 'Chest'), ('Back', 'Back'), ('Legs', 'Legs'), ('Shoulders', 'Shoulders'), ('Cardio', 'Cardio')], default='Full Body', max_length=20),
        ),
    ]
