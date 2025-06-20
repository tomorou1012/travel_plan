from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Member, Comment, Post, Day, Schedule
from django.forms import inlineformset_factory



class MemberForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ['username', 'password1', 'password2', 'birth_date', 'about_me', 'member_image']

class MemberUpdateForm(UserChangeForm):
    password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput,
        required=False,
    )        
    password2 = forms.CharField(
        label='新しいパスワード（確認用）',
        widget=forms.PasswordInput,
        required=False,
        help_text='確認のため、もう一度新しいパスワードを入力してください'
    )

    class Meta:
        model = Member
        fields = ['username', 'birth_date', 'about_me', 'member_image']
        widgets = {
            'member_image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*',
            }),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})

        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['place', 'prefecture']

class DayForm(forms.ModelForm):
    class Meta:
        model = Day
        fields = ['date', 'weather']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['time', 'activity']
        widgets = {
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'activity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'アクティビティ'
            })
        }

def get_day_formset(extra=1):
    return inlineformset_factory(
        Post,
        Day,
        form=DayForm,
        fields=['date', 'weather'],
        extra=extra,
        can_delete=True
    )

def get_schedule_formset(extra=1):
    return inlineformset_factory(
        Day,
        Schedule,
        form=ScheduleForm,
        fields=['time', 'activity'],
        extra=extra,
        can_delete=True
    )