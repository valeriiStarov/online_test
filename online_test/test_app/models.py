from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Prefetch



class TestGroup(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    logging_required = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('test_group', kwargs={'test_group_pk': self.pk})

    def get_test_group_statistics_url(self):
        return reverse('test_group_statistics', kwargs={'test_group_pk': self.pk})



class Test(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    test_group = models.ForeignKey('TestGroup', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('test', kwargs={'test_pk': self.pk})


class Question(models.Model):
    text = models.TextField()
    test = models.ForeignKey('Test', on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return f'{self.text} - {self.pk}'


class Answer(models.Model):
    text = models.CharField(max_length=150)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return self.text


class AnswerFromUser(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'pk = {self.pk}'


class TestStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, blank=True)
    number_of_correct_answers = models.PositiveSmallIntegerField(default=0)
    number_of_questions = models.PositiveSmallIntegerField(blank=True)

    def __str__(self) -> str:
        return f'Statistic for user {self.user} in {self.test}'

    def get_absolute_url(self):
        return reverse('statistics', kwargs={'stat_pk': self.pk})


class AnswerFromAnon(models.Model):
    key = models.UUIDField()
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return f'pk = {self.pk}'


class AnonTestStatistics(models.Model):
    key = models.UUIDField()
    test = models.ForeignKey('Test', on_delete=models.CASCADE, blank=True)
    number_of_correct_answers = models.PositiveSmallIntegerField(default=0)
    number_of_questions = models.PositiveSmallIntegerField(blank=True)

    def __str__(self) -> str:
        return f'Statistic for anon with key - {self.key} in {self.test}'

    def get_absolute_url(self):
        return reverse('statistics', kwargs={'stat_pk': self.key})


