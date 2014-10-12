from django import forms
from django.contrib import admin

# Register your models here.
from django.contrib.admin.widgets import FilteredSelectMultiple

from learn.models import Quiz, Course, Progress, Question, UserProfile, MCQuestion, Answer,TF_Question,Essay_Question

class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):

    class Meta:
        model = Quiz

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Questions',
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial =\
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set = self.cleaned_data['questions']
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', 'course', )
    list_filter = ('course',)
    search_fields = ('description', 'course', )


class CourseAdmin(admin.ModelAdmin):
    search_fields = ('course', )

	
class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'course', )
    list_filter = ('course',)
    fields = ('content', 'course', 'quiz', 'explanation')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]



class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'course', )
    list_filter = ('course',)
    fields = ('content', 'course', 'quiz', 'explanation', 'correct',)

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

	

admin.site.register(Course, CourseAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(TF_Question, TFQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)


