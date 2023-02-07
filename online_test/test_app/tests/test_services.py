from django.test import TestCase

from test_app.services import *
from test_app.models import *


class ServicesTest(TestCase):

    def test_tests_groups_with_test(self):
        """
        Возвращает только группы с тестами, вопросами и ответами
        """
        test_group_1 = TestGroup.objects.create(title='1')
        test_1 = Test.objects.create(test_group=test_group_1)
        question_1 = Question.objects.create(test=test_1)
        answer_1 = Answer.objects.create(question=question_1)
        
        test_group_2 = TestGroup.objects.create(title='2')
        test_2 = Test.objects.create(test_group=test_group_2)
        question_2 = Question.objects.create(test=test_2)

        test_group_3 = TestGroup.objects.create(title='3')
        test_3 = Test.objects.create(test_group=test_group_3)

        test_group_4 = TestGroup.objects.create(title='4')

        with_test = tests_groups_with_test()
        self.assertEqual(with_test[0], test_group_1)
