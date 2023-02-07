from django.shortcuts import render
from django.views.generic import ListView, CreateView, View, DetailView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.shortcuts import redirect


from .models import *
from .forms import *
from .services import *


class Home(ListView):
    template_name: str = 'test_app/home.html'
    model = TestGroup
    context_object_name = 'test_groups'

    def get_queryset(self):
        return tests_groups_with_test()
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context


class TestGroupView(View):
    template_name: str = 'test_app/test_group.html'
    title = 'Группа тестов'

    def get(self, request, *args, **kwargs):
        test_group_pk = self.kwargs['test_group_pk']
        
        access_denied(request=request, test_group_pk=test_group_pk)
            
        test_group = make_test_group(test_group_pk=test_group_pk)
        
        tests = tests_with_questions(test_group_pk)

        if_no_auth_create_session(request=request)

        passed = tests_previous_passed(request=request,
                                       tests=tests)

        tests_done = tests_have_statistics(request=request,
                                           test_group_pk=test_group_pk)
        
        all_done = all_tests_done(request=request, tests=tests)
        
        return render(
            request,
            template_name=self.template_name,
            context={
                'title': self.title,
                'tests': tests,
                'test_group': test_group,
                'passed': passed,
                'tests_done': tests_done,
                'all_done': all_done
            }
        )
            

class TestView(View):
    template_name: str = 'test_app/test.html'
    title = 'Тест'

    def get(self, request, *args, **kwargs):
        test_pk = self.kwargs['test_pk']
        
        page_object = question_page_object(request=request, test_pk=test_pk)

        answers = Answer.objects.filter(question__pk=page_object.object_list[0].pk)
        
        delete_previous_answers(request=request, answers=answers)
        # В данном проекте не стояла задача запоминать старые ответы от пользователей и показывать их пользователю, поэтому старые ответы просто удаляются если пользователь заново проходит тест.

        return render(
            request,
            template_name=self.template_name,
            context={
                'title': self.title,
                'questions': page_object,
                'answers': answers,
                'form': AnswerForm(form_count=int(answers.count()))
            }
        )
            

    def post(self, request, **kwargs):
        test_pk = self.kwargs['test_pk']
        form = AnswerForm(request.POST)
        
        page_object = question_page_object(request=request, test_pk=test_pk)

        answers = Answer.objects.filter(
            question__pk=page_object.object_list[0].pk)

        if form.is_valid():
            answers = answers_from_user_or_anon(answers=answers,
                                                     form=form)

            save_answers_from_user_or_anon(request=request, answers=answers)

            if page_object.has_next():
                next_page = verified_next_page(request=request)
                return redirect(f"/test/{test_pk}?page={next_page}")
            else:    
                create_or_update_test_statistics(
                    request=request, 
                    number_of_questions=page_object.paginator.count,
                    number_of_correct_answers = \
                        number_of_correct_answers(request=request, 
                                                  test_pk=test_pk),
                    test_pk=test_pk
                    )

                delete_answers(request)

                stat_pk = statistics_number(request=request, test_pk=test_pk)
                return redirect(f'/statistics/{stat_pk}')
        else:
            return render(
                request,
                template_name=self.template_name,
                context={
                    'title': self.title,
                    'questions': page_object,
                    'answers': answers,
                    'form': AnswerForm(
                        form_count=int(answers.count())),
                    'form_error': form
                }
            )


class TestStatisticsView(View):
    template_name: str = 'test_app/statistics.html'
    title = 'Статистика за тест'

    def get(self, request, *args, **kwargs):
        stat_pk = self.kwargs['stat_pk']
        statistics = test_statistics(request=request, stat_pk=stat_pk)

        wrong_answers = number_of_wrong_answers(
            statistics.number_of_questions,
            statistics.number_of_correct_answers
        )

        percentege_of_correct = percentage_of_correct_answers(
            statistics.number_of_questions,
            statistics.number_of_correct_answers
        )

        test_group = statistics.test.test_group

        return render(
            request,
            template_name=self.template_name,
            context={
                'title': self.title,
                'statistics': statistics,
                'wrong_answers': wrong_answers,
                'percentege_of_correct': percentege_of_correct,
                'test_group': test_group
            }
        )


class TestGroupStatistics(View):
    template_name: str = 'test_app/test_group_statistics.html'
    title = 'Статистика за все тесты'
    
    def get(self, request, *args, **kwargs):
        test_group_pk = self.kwargs['test_group_pk']

        access_denied(request=request, test_group_pk=test_group_pk)

        test_group = TestGroup.objects.get(pk=test_group_pk)
        
        stat_group = statistics_group(request=request, 
                                      test_group_pk=test_group_pk)

        gen_stat = general_statistics(stat_group=stat_group)

        wrong_answers = number_of_wrong_answers(
            gen_stat['number_of_questions'],
            gen_stat['number_of_correct_answers']
        )
        percentege_of_correct = percentage_of_correct_answers(
            gen_stat['number_of_questions'],
            gen_stat['number_of_correct_answers']
        )

        return render(
            request,
            template_name=self.template_name,
            context={
                'title': self.title,
                'test_group': test_group,
                'number_of_correct_answers': 
                    gen_stat['number_of_correct_answers'],

                'wrong_answers': wrong_answers,
                'percentege_of_correct': percentege_of_correct
            }
        )


class RegisterUser(CreateView):
    template_name = 'test_app/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    template_name = 'test_app/login.html'
    form_class = LoginUserForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Логин'
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('home')