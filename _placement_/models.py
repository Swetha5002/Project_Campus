from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import os

def get_current_year():
    return timezone.now().year

class User(AbstractUser):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    )
    
    # Personal Information
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    university_number = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.SET_NULL,
        related_name='students',
        blank=True, 
        null=True
    )
    section = models.ForeignKey(
        'Section',
        on_delete=models.SET_NULL,
        related_name='students',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        default=timezone.datetime(2000, 1, 1).date(),
        blank=True, 
        null=True
    )
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
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
    
    # Professional Information
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    
    # Coding Platform Links (separate fields)
    leetcode_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="LeetCode Profile")
    codechef_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="CodeChef Profile")
    hackerrank_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="HackerRank Profile")

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['batch', 'name']
        indexes = [
            models.Index(fields=['batch']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.university_number})" if self.name else self.username

    def delete(self, *args, **kwargs):
        if self.profile_image and os.path.isfile(self.profile_image.path):
            os.remove(self.profile_image.path)
        super().delete(*args, **kwargs)

class Batch(models.Model):
    class Department(models.TextChoices):
        ECE = 'ECE', 'Electronics and Communication Engineering'
        CSE = 'CSE', 'Computer Science and Engineering'
        ME = 'ME', 'Mechanical Engineering'
        CE = 'CE', 'Civil Engineering'
        EE = 'EE', 'Electrical Engineering'
        IT = 'IT', 'Information Technology'
        EEE = 'EEE', 'Electrical and Electronics Engineering'
        AIDS = 'AIDS', 'Artificial Intelligence and Data Science'
 
    current_year = get_current_year()
    YEAR_RANGE = range(current_year , current_year + 5)
    End_YEAR_CHOICES = [(r, r) for r in YEAR_RANGE]
    
    department = models.CharField(
        max_length=10,
        choices=Department.choices,
        default=Department.ECE,
        blank=True,
        null=True
    )
    end_year = models.PositiveSmallIntegerField(
        choices=End_YEAR_CHOICES,
        default=current_year + 4,
        validators=[MinValueValidator(2000), MaxValueValidator(current_year + 5)],
        blank=True,
        null=True
    )
    batch_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='administered_batches',
        blank=True,
        null=True,
        limit_choices_to={'is_superuser': True}
    )
    
    class Meta:
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'
        ordering = ['department', 'end_year']
        unique_together = ['department', 'end_year']

    
    def __str__(self):
        return f"{self.department} {self.end_year}"

    def save(self, *args, **kwargs):
        if self.batch_admin and not self.batch_admin.is_superuser:
            raise ValueError("Batch admin must be a superuser")
        super().save(*args, **kwargs)

class Section(models.Model):
    class Name(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'
        E = 'E', 'E'
    
    name = models.CharField(max_length=10, choices=Name.choices)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='sections')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['batch', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'batch'],
                name='unique_section_per_batch'
            )
        ]

    def __str__(self):
        return f"{self.name} {self.batch}"

class QuestionPaper(models.Model):
    paper_code = models.CharField(max_length=10, unique=True)
    paper_title = models.CharField(max_length=255)
    paper_description = models.TextField(blank=True, null=True)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes")
    no_of_qs = models.PositiveIntegerField(blank=True, null=True)
    total_marks = models.PositiveIntegerField(blank=True, null=True)
    is_practice_paper = models.BooleanField(default=True)
    is_assessment_paper = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.paper_title} ({self.paper_code})"

    def get_absolute_url(self):
        return reverse('question_paper_preview', args=[self.pk])

    class Meta:
        verbose_name = "Question Paper"
        verbose_name_plural = "Question Papers"

class Question(models.Model):
    CORRECT_OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    question_paper = models.ForeignKey(
        QuestionPaper, related_name='questions', on_delete=models.CASCADE
    )
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_text = models.TextField()
    mark = models.PositiveIntegerField(default=1)
    option_A = models.TextField()
    option_B = models.TextField()
    option_C = models.TextField()
    option_D = models.TextField()
    correct_option = models.CharField(
        default='A',
        max_length=1,
        choices=CORRECT_OPTION_CHOICES,
        help_text="Key of the correct option for MCQs."
    )

    def __str__(self):
        return f"Question {self.pk} ({self.question_paper.paper_code})"

    def clean(self):
        super().clean()
        if not all([self.option_A, self.option_B, self.option_C, self.option_D, self.correct_option]):
            raise ValueError("MCQs must have all four options and a correct option selected.")

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

class Material(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('material_detail', args=[self.pk])

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"

class StudentResults(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Malpractice', 'Malpractice'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='results')
    test_title = models.CharField(max_length=255, default='')
    test_code = models.CharField(max_length=10, default='')  
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    attended = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
    date_of_exam = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"Result for {self.user} - {self.test_code}"

    class Meta:
        verbose_name = "Student Result"
        verbose_name_plural = "Student Results"

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
    package = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    placement_year = models.PositiveIntegerField(validators=[MinValueValidator(2000)])
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
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

# Signals
@receiver(post_delete, sender=User)
def delete_user_profile_image(sender, instance, **kwargs):
    if instance.profile_image and os.path.isfile(instance.profile_image.path):
        os.remove(instance.profile_image.path)

@receiver(post_save, sender=User)
def assign_user_to_batch_group(sender, instance, created, **kwargs):
    if created and instance.batch:  # Changed from instance.batch_year
        group_name = f"Batch {instance.batch.end_year}"  # Now using batch.end_year
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)

@receiver(post_delete, sender=PlacementStories)
def delete_story_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
        
        
# models.py
class MistakenQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Assuming you have a Question model
    test_code = models.CharField(max_length=100)
    selected_option = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'question', 'test_code')