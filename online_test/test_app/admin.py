from django.contrib import admin
from django.utils.html import format_html
from .models import *
from .forms import *


class QuestionInline(admin.StackedInline):
    model = Question
    extra: int = 0
    fields = ['get_edit_link', 'text']
    readonly_fields = ['get_edit_link']

    def get_edit_link(self, instance):
        url = f'http://127.0.0.1:8000/admin/test_app/question/{instance.pk}/change/'
        return format_html('<a href="{}">Редактировать вопрос, изменить ответы</a>', url)

    get_edit_link.short_description = 'Link to edit'

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    save_on_top: bool = True
    fields = ['title', 'description']
    inlines = [QuestionInline]


class TestInline(admin.StackedInline):
    save_on_top: bool = True
    model = Test
    extra: int = 0
    fields = ['get_edit_link', 'title', 'description']
    readonly_fields = ['get_edit_link']

    def get_edit_link(self, instance):
        url = f'http://127.0.0.1:8000/admin/test_app/test/{instance.pk}/change/'
        return format_html('<a href="{}">Редактировать тест, изменить вопросы</a>', url)

    get_edit_link.short_description = 'Link to edit'

@admin.register(TestGroup)
class TestGroupAdmin(admin.ModelAdmin):
    save_on_top: bool = True
    inlines = [TestInline]
    fields = ['title', 'description', 'logging_required']


class AnswerInline(admin.StackedInline):
    form = AnswerAdminForm
    model = Answer
    extra: int = 0



@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    save_on_top: bool = True
    fields = ['text', 'correct', 'question']

    

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    save_on_top: bool = True
    fields = ['text', 'test']
    inlines = [AnswerInline]

admin.site.register(AnswerFromUser)
admin.site.register(TestStatistics)
admin.site.register(AnswerFromAnon)
admin.site.register(AnonTestStatistics)

