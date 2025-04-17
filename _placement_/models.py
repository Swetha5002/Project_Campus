from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import os

def get_current_year():
    return timezone.now().year

class User(AbstractUser):
    # Constants
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    )
    
    # Personal Information
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Fixed typo: upload_to
    university_number = models.PositiveIntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    batch_year = models.PositiveSmallIntegerField(
        default=2026,
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(get_current_year() + 5)  # Fixed lambda issue
        ],
        blank=True, 
        null=True
    )
    section = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(
        default=timezone.datetime(2000, 1, 1).date(),
        blank=True, 
        null=True
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        blank=True,
        null=True
    )
    
    # Academic Information
    cgpa = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        blank=True,
        null=True
    )
    average_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        blank=True,
        null=True
    )
    
    # Professional Links
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    
    # Code Platforms
    code_platforms = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="List of dictionaries containing 'platform_name' and 'profile_link'"
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='placement_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='placement_user_permissions',
        blank=True
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['batch_year', 'name']
        indexes = [
            models.Index(fields=['batch_year']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.university_number})" if self.name else self.username

    def delete(self, *args, **kwargs):
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
        super().delete(*args, **kwargs)

# Signal to delete profile image on User deletion
@receiver(post_delete, sender=User)
def delete_user_profile_image(sender, instance, **kwargs):
    if instance.profile_image and os.path.isfile(instance.profile_image.path):
        os.remove(instance.profile_image.path)

@receiver(post_save, sender=User)
def assign_user_to_batch_group(sender, instance, created, **kwargs):
    if created and instance.batch_year:
        group_name = f"Batch {instance.batch_year}"
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)


class StudentResults(models.Model):
    STATUS_CHOICES = (
        ('C', 'Completed'),
        ('M', 'Malpractice'),
        ('A', 'Absent'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='results'
    )
    test_code = models.CharField(max_length=20, db_index=True)
    test_title = models.CharField(max_length=255)
    date_of_exam = models.DateField()
    time = models.TimeField()
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='C'
    )
    attended = models.BooleanField(default=False)
    max_marks = models.FloatField(blank=True, null=True)  # Added missing field
    obtained_marks = models.FloatField(blank=True, null=True)  # Added missing field

    class Meta:
        verbose_name = 'Student Result'
        verbose_name_plural = 'Student Results'
        ordering = ['-date_of_exam', '-time']
        unique_together = ['user', 'test_code']
        indexes = [
            models.Index(fields=['-date_of_exam', '-time']),
        ]

    def __str__(self):
        return f"{self.user.name if self.user.name else self.user.username} - {self.test_title} ({self.percentage}%)"

    def save(self, *args, **kwargs):
        if self.max_marks and self.obtained_marks:
            self.percentage = (self.obtained_marks / self.max_marks) * 100
        super().save(*args, **kwargs)


class PlacementStories(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    image = models.ImageField(
        upload_to='placement_story_images/%Y/%m/%d/',
        blank=True,
        null=True,
        max_length=500
    )
    company = models.CharField(max_length=255, db_index=True)
    package = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    placement_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000)]
    )
    linkedin_profile = models.URLField(max_length=500, blank=True)
    story = models.TextField()
    
    story_narrator_keyTakeaways = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="List of key takeaways from the story"
    )
    
    def clean(self):
        if self.placement_year > get_current_year() + 1:
            raise ValidationError("Placement year cannot be in the future.")

    class Meta:
        verbose_name_plural = "Placement Stories"
        ordering = ['-placement_year', 'company']
        indexes = [
            models.Index(fields=['company', 'placement_year']),
            models.Index(fields=['-placement_year']),
        ]

    def __str__(self):
        return f"{self.name} - {self.company} ({self.placement_year})"

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

# Signal to delete story image on PlacementStories deletion
@receiver(post_delete, sender=PlacementStories)
def delete_story_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


class Class(models.Model):
    name = models.CharField(max_length=100, unique=True)
    batch_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(get_current_year() + 5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ['batch_year', 'name']

    def __str__(self):
        return f"{self.name} ({self.batch_year})"