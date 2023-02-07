from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Answer, AnswerFromUser


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control',
    'placeholder':'email@email.com'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль должен содержать как минимум 8 символов'}))
    password2 = forms.CharField(label='Подтверждение нового пароля', widget=forms.PasswordInput(attrs=
    {'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise ValidationError("Данный email уже зарегистрирован")
        return email


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'class': 'form-control'})
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        user = self.cleaned_data['username']
        try:
            User.objects.get(username=user)
        except User.DoesNotExist:
            raise ValidationError("Данный пользователь не зарегистрирован")
        return user


class AnswerForm(forms.Form):
    class Meta:
        model = AnswerFromUser
        fields = ('correct_from_user',)
        

    def __init__(self, *args, **kwargs):
        form_count = kwargs.pop('form_count', None)
        super(AnswerForm, self).__init__(*args, **kwargs)

        if form_count:
            for i in range(1, form_count + 1):
                self.fields[f'correct_from_user_{i}'] = forms.BooleanField(required=False)

    def clean(self):
        data = super(AnswerForm, self).clean()
        check_list = []
        for data in self.data:
            if data.startswith('correct_from_user'):
                check_list.append(data)
        if check_list == []:
            raise ValidationError('Сначала необходимо ответить')
        return data
                

class AnswerAdminForm(forms.ModelForm):
    buffer_list = []
    
    class Meta:
        model = Answer
        fields = ['text', 'correct', 'question']
       

    def clean(self):
        
        count_forms = self.data['answer_set-TOTAL_FORMS']
        if len(self.buffer_list) < int(count_forms)-1:
            self.buffer_list.append(self.cleaned_data['correct'])
        else:
            self.buffer_list.append(self.cleaned_data['correct'])
            if self.buffer_list.count(self.buffer_list[0]) == len(self.buffer_list):
                self.buffer_list.clear()
                raise ValidationError('Все ответы не могут быть правильными, также все ответы не могут быть неправильными')
            else:
                self.buffer_list.clear()
            
