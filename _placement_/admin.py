from django.contrib import admin
from .models import User, StudentResults, PlacementStories, QuestionPaper, Question, Material, Batch, Section

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'get_batch_year', 'get_section')
    search_fields = ('username', 'name', 'university_number')
    list_filter = ('batch__end_year', 'gender', 'batch__department')
    raw_id_fields = ('batch', 'section')
    
    def get_batch_year(self, obj):
        return obj.batch.end_year if obj.batch else None
    get_batch_year.short_description = 'Batch Year'
    get_batch_year.admin_order_field = 'batch__end_year'
    
    def get_section(self, obj):
        return obj.section.name if obj.section else None
    get_section.short_description = 'Section'

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('department', 'end_year', 'batch_admin')
    list_filter = ('department', 'end_year')
    search_fields = ('department', 'end_year')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch')
    list_filter = ('batch',)
    search_fields = ('name', 'batch__department')

@admin.register(StudentResults)
class StudentResultsAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_code', 'percentage', 'status', 'date_of_exam')
    list_filter = ('status', 'date_of_exam')
    search_fields = ('user__username', 'test_code')

@admin.register(PlacementStories)
class PlacementStoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'package', 'placement_year')
    list_filter = ('placement_year', 'company')
    search_fields = ('name', 'company')

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = (
        'paper_code',
        'paper_title',
        'time_limit',
        'no_of_qs',
        'total_marks',
    )
    search_fields = ('paper_code', 'paper_title')
    list_filter = ('paper_code', 'paper_title')
    inlines = [QuestionInline]
    ordering = ('paper_code',)
    fieldsets = (
        (None, {
            'fields': ('paper_code', 'paper_title', 'paper_description')
        }),
        ('Settings', {
            'fields': ('time_limit', 'no_of_qs', 'total_marks')
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_paper', 'serial_number', 'question_text', 'mark', 'get_correct_answer')
    search_fields = ('question_text',)
    list_filter = ('question_paper', 'question_paper__paper_code')
    ordering = ('question_paper',)

    def serial_number(self, obj):
        return list(self.model.objects.all()).index(obj) + 1
    serial_number.short_description = 'S.No'

    def get_correct_answer(self, obj):
        correct_option_mapping = {
            'A': obj.option_A,
            'B': obj.option_B,
            'C': obj.option_C,
            'D': obj.option_D,
        }
        return correct_option_mapping.get(obj.correct_option, "N/A")
    get_correct_answer.short_description = 'Correct Answer'

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)