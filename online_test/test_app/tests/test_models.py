from django.test import TestCase

from test_app.models import *


class ModelTest(TestCase):

    def test_test_group_str(self):
        """
        Проверка на правильность метода __str__
        """
        test_group = TestGroup.objects.create(title='Тест группа 1')

        self.assertEqual(str(test_group), 'Тест группа 1')

    def test_test_group_get_absolute_url(self):
        """
        Проверка на правильный url
        """
        test_group = TestGroup.objects.create(title='Тест группа 1')
        self.assertEqual(test_group.get_absolute_url(), f'/test_group/{test_group.pk}')

    def test_get_test_group_statistics_url(self):
        """
        Проверка на правильный url для статистики по группам
        """
        test_group = TestGroup.objects.create(title='Тест группа 1')
        self.assertEqual(test_group.get_test_group_statistics_url(), f'/statistics/test_group/{test_group.pk}')

# Остальные тесты по моделям аналогичны
