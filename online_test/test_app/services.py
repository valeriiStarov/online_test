from django.core.paginator import Paginator, Page
from django.db.models.query import QuerySet
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.http import Http404
import uuid

from .models import *
from .forms import *


def tests_groups_with_test() -> list[TestGroup]:
    """
    Возвращает список наборов тестов, которые имеют внутри хотябы один тест с вопросом и ответами.
    """
    tests_groups = []
    tests = Test.objects.select_related('test_group')
    questions = Question.objects.select_related('test')
    answers = Answer.objects.select_related('question')
    for test in tests:
        if test.test_group not in tests_groups:
            for question in questions:
                if question.test == test:
                    for answer in answers:
                        if answer.question == question:
                            tests_groups.append(test.test_group)
                            break
                    break
    return tests_groups


def tests_with_questions(test_group_pk: int) -> list[Test]:
    """
    Возвращает список тестов, которые имеют хотябы один вопрос с ответами.
    """
    test_list = []
    
    tests = Test.objects.filter(test_group__pk=test_group_pk).select_related()
    questions = Question.objects.select_related('test')
    answers = Answer.objects.select_related('question')
    
    for question in questions:
        if question.test in tests:
            if question.test not in test_list:
                for answer in answers:
                    if answer.question == question:
                        test_list.append(question.test)
                        break
    return test_list


def tests_previous_passed(request, tests) -> list[Test]:
    """
    Возвращает список тестов у которых предыдущий тест пройден.
    """
    passed_tests = []
    statistics_exist = False
    if request.user.is_authenticated:
        for test in tests:
            if statistics_exist == True:
                passed_tests.append(test)
            
            try:
                TestStatistics.objects.get(test=test, user=request.user)
                statistics_exist = True
            except ObjectDoesNotExist:
                statistics_exist = False
    else:
        for test in tests:
            if statistics_exist == True:
                passed_tests.append(test)
            try:
                AnonTestStatistics.objects.get(key=request.session['anon_pk'],
                                               test=test)
                
                statistics_exist = True
            except ObjectDoesNotExist:
                statistics_exist = False

    return passed_tests


def all_tests_done(request, tests: list[Test]) -> bool:
    """
    Возвращает True если все тесты пройдены
    """
    all_done = False
    if len(tests) == 0:
        raise Http404('В данном наборе нет тестов')
    if request.user.is_authenticated:
        try:
            TestStatistics.objects.get(
                    test=tests[-1],
                    user=request.user)
            all_done = True
        except ObjectDoesNotExist:
            pass
    else:
        try:
            AnonTestStatistics.objects.get(
                    test=tests[-1],
                    key=request.session['anon_pk'])
            all_done = True
        except ObjectDoesNotExist:
            pass
    return all_done


def question_page_object(request, test_pk: int) -> Page:
    """
    Возвращает страницу с объектом для вывода Вопросов по одному на странице
    """
    questions = Question.objects.filter(test__pk=test_pk).order_by('pk')
    paginator = Paginator(questions, per_page=1)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    return page_object


def delete_previous_answers(request, 
                            answers: QuerySet[Answer]) -> None:
    """
    Если у пользователя есть старые ответы, то они удаляются чтобы далее записать новые.
    """
    if request.user.is_authenticated:
        for answer in answers:
            AnswerFromUser.objects.filter(answer = answer,
                                          user = request.user).delete()
    else:
        try:
            for answer in answers:
                AnswerFromAnon.objects.filter(
                                            answer = answer,
                                            key = request.session['anon_pk']
                                            ).delete()
        except KeyError:
            raise PermissionDenied()
            

def answers_from_user_or_anon(answers: QuerySet[Answer], 
                      form: AnswerForm) -> list[Answer]:
    """
    Возвращает список объектов Answer от пользователя
    """
    numbers_of_answers_from_user = []
    for f in form.data:
        if f.startswith('correct_from_user'):
            numbers_of_answers_from_user.append(int(f[-1]))

    user_answers = []
    list_of_answers = [answer for answer in answers]
    for number in numbers_of_answers_from_user:
        if list_of_answers[number-1]:
            user_answers.append(list_of_answers[number-1])
            
    return user_answers


def save_answers_from_user_or_anon(request, answers: list[Answer]) -> None:
    """
    Сохранение в БД выбранных ответов от пользователя
    """
    if request.user.is_authenticated:
        for answer in answers:
            AnswerFromUser.objects.create(answer = answer,
                                          user = request.user)
                    
    else:
        for answer in answers:
            AnswerFromAnon.objects.create(answer = answer,
                                          key = request.session['anon_pk'])
                


def verified_next_page(request):
    """
    Обрабатывает исключение для перехода с первой странице на вторую и возвращает номер следующей страницы.
    """
    # Так как при открытии теста получается адрес: 
    # '/test/1', а не '/test/1?page=1', то переход на вторую страницу выдает ошибку MultiValueDictKeyError.
    try:
        page = int(request.GET['page'])
        next_page = page + 1
    except MultiValueDictKeyError:
        next_page = 2
    return next_page


def correct_and_users_answers(request, question: Question) -> dict:
    """
    Возвращает словарь с правильными ответами и ответами пользователя.
    """
    correct_answers = []
    users_answers = []
    answers_on_question = Answer.objects.filter(
                        question__pk=question.pk)

    if request.user.is_authenticated:
        for answer in answers_on_question:
            correct_answers.append(answer.correct)

            try:
                AnswerFromUser.objects.get(answer__pk=answer.pk)
                users_answers.append(True)
            except ObjectDoesNotExist:
                users_answers.append(False)
    else:
        for answer in answers_on_question:
            correct_answers.append(answer.correct)

            try:
                AnswerFromAnon.objects.get(answer__pk=answer.pk,
                                           key=request.session['anon_pk'])
                users_answers.append(True)
            except ObjectDoesNotExist:
                users_answers.append(False)

    return {'correct_answers': correct_answers, 
            'users_answers': users_answers}


def number_of_correct_answers(request, test_pk: int) -> int:
    """
    Возвращает число правильных ответов в тесте.
    """
    questions = Question.objects.filter(test__pk=test_pk).order_by('pk')

    number_of_correct_answers = 0
    for question in questions:

        dict_answers: dict = correct_and_users_answers(request, question)

        if dict_answers['correct_answers'] == \
                dict_answers['users_answers']:
            number_of_correct_answers += 1
    return number_of_correct_answers


def create_or_update_test_statistics(request, 
                                     number_of_questions: int, 
                                     number_of_correct_answers: int, 
                                     test_pk: int) -> None:
    """
    Создает или обновляет статистику за тест для user или anon
    """
    if request.user.is_authenticated:
        try:
            answer_statistic = TestStatistics.objects.get(
                        user = request.user,
                        test = Test.objects.get(pk=test_pk),
                        number_of_questions = number_of_questions,
                        )
            answer_statistic.number_of_correct_answers = number_of_correct_answers
            answer_statistic.save()
        except ObjectDoesNotExist:
            answer_statistic = TestStatistics.objects.create(
                        user = request.user,
                        test = Test.objects.get(pk=test_pk),
                        number_of_questions = number_of_questions,
                        number_of_correct_answers = number_of_correct_answers
                        )
    else:
        try:
            answer_statistic = AnonTestStatistics.objects.get(
                        key = request.session['anon_pk'],
                        test = Test.objects.get(pk=test_pk),
                        number_of_questions = number_of_questions,
                        )
            answer_statistic.number_of_correct_answers = number_of_correct_answers
            answer_statistic.save()
        except ObjectDoesNotExist:
            answer_statistic = AnonTestStatistics.objects.create(
                        key = request.session['anon_pk'],
                        test = Test.objects.get(pk=test_pk),
                        number_of_questions = number_of_questions,
                        number_of_correct_answers = number_of_correct_answers
                        )



def number_of_wrong_answers(number_of_questions: int, number_of_correct_answers: int) -> int:
    """
    Возвращает число неправильных ответов.
    """
    return int(number_of_questions - number_of_correct_answers)


def percentage_of_correct_answers(number_of_questions: int, number_of_correct_answers: int) -> str:
    """
    Возвращает процент правильных ответов.
    """
    try:
        check = 1/number_of_questions
    except ZeroDivisionError:
        return ''
    return str(round(float(number_of_correct_answers * 100 / number_of_questions), 2)) + ' %'


def statistics_group(request, test_group_pk: int) -> list[TestStatistics]:
    """
    Возвращает список объектов статистики за все тесты по данной теме.
    """
    
    tests = tests_with_questions(test_group_pk=test_group_pk)
    if len(tests) == 0:
        raise Http404('Для данного набора нет тестов')
    statistics_group = []
    if request.user.is_authenticated:
        for test in tests:
            try:
                statistics_group.append(TestStatistics.objects.get(
                    user = request.user,
                    test = test
                ))
            except ObjectDoesNotExist:
                pass
    else:
        for test in tests:
            try:
                statistics_group.append(AnonTestStatistics.objects.get(
                    key = request.session['anon_pk'],
                    test = test
                ))
            except KeyError:
                raise PermissionDenied()
            except AnonTestStatistics.DoesNotExist:
                raise Http404('У вас еще нет статистики по данной теме')
    return statistics_group


def general_statistics(stat_group: list[TestStatistics]) -> dict:
    """
    Возвращает словарь с количеством правильных ответов и количеством вопросов за все тесты по данной теме.
    """
    number_of_correct_answers = 0
    number_of_questions = 0
    for statistics in stat_group:
        number_of_correct_answers += statistics.number_of_correct_answers
        number_of_questions += statistics.number_of_questions

    return {'number_of_correct_answers': number_of_correct_answers,
            'number_of_questions': number_of_questions}


def delete_answers(request) -> None:
    """
    Удаляет ответы пользователя или анона из базы
    """
    if request.user.is_authenticated:
        AnswerFromUser.objects.filter(user=request.user).delete()
    else:
        AnswerFromAnon.objects.filter(key=request.session['anon_pk']).delete()


def statistics_number(request, test_pk: int) -> int:
    """
    Возвращает номер статистики за тест
    """
    if request.user.is_authenticated:
        stat_pk = TestStatistics.objects.get(
                    user=request.user, test = Test.objects.get(pk=test_pk)).pk
    else:
        stat_pk = AnonTestStatistics.objects.get(
                    key=request.session['anon_pk'], test = Test.objects.get(pk=test_pk)).pk
    return stat_pk


def test_statistics(request, stat_pk: int) -> TestStatistics | \
                                              AnonTestStatistics:
    """
    Возвращает статистику за тест
    """
    if request.user.is_authenticated:
        statistics = TestStatistics.objects.get(pk=stat_pk,
                                        user=request.user)
    else:
        try:
            statistics = AnonTestStatistics.objects.get(
                                                pk=stat_pk,
                                                key=request.session['anon_pk']
                                                )
        except KeyError:
            raise PermissionDenied()

    return statistics


def if_no_auth_create_session(request) -> None:
    """
    Если пользователь не авторизован, создает для него идентификатор сессии - anon_pk.
    """
    try:
        request.session['anon_pk']
    except KeyError:
        if not request.user.is_authenticated:
            request.session['anon_pk'] = str(uuid.uuid4())


def tests_have_statistics(request, test_group_pk: int) -> list:
    """
    Возвращает список пройденных тестов.
    """
    tests_done = []
    tests = Test.objects.filter(test_group__pk=test_group_pk)
    if request.user.is_authenticated:
        for test in tests:
            try:
                TestStatistics.objects.get(test=test, user = request.user)
                tests_done.append(test)
            except ObjectDoesNotExist:
                pass
    else:
        for test in tests:
            try:
                AnonTestStatistics.objects.get(test=test, 
                                               key=request.session['anon_pk'])
                tests_done.append(test)
            except ObjectDoesNotExist:
                pass
    return tests_done



def make_test_group(test_group_pk: int) -> TestGroup | None:
    """
    Возвращает TestGroup текущего набора.
    """
    test = Test.objects.select_related('test_group').filter(test_group__pk=test_group_pk).first()
    if test is not None:
        return test.test_group


def access_denied(request, test_group_pk: int) -> None:
    """
    Реизит 403 Forbidden
    """
    try:
        test_group = TestGroup.objects.get(pk=test_group_pk)
    except TestGroup.DoesNotExist:
        raise Http404('Данная тема не существует')
    if not request.user.is_authenticated and bool(test_group.logging_required):
        raise PermissionDenied()