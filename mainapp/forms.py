from django import forms
from django.core.mail import EmailMultiAlternatives
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


from .models import Post, Response, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            # 'author',
            'title',
            'text',
            'category'
            ]


class ResponseForm(forms.ModelForm):

    class Meta:
        model = Response
        fields = [
            'text'
        ]


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        registered_users = Group.objects.get(name='registered users')
        user.groups.add(registered_users)

        subject = 'Добро пожаловать на наш ресурс одной известной MMORPG!'
        text = f'{user.username}, вы успешно зарегистрировались на сайте!'
        html = (
            f'<b>{user.username}</b>, вы успешно зарегистрировались на '
            f'<a href="http://127.0.0.1:8000/posts">сайте</a>!'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        return user
