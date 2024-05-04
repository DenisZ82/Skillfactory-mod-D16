from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from ckeditor_uploader.fields import RichTextUploadingField


class User(AbstractUser):
    code = models.CharField(max_length=10, blank=True, null=True)


class Post(models.Model):
    CATEGORY = [
        ('tanks', 'Танки'),
        ('healers', 'Хилы'),
        ('dd', 'ДД'),
        ('merchants', 'Торговцы'),
        ('guildmasters', 'Гильдмастер'),
        ('questgivers', 'Квестгиверы'),
        ('smiths', 'Кузнецы'),
        ('tanners', 'Кожевенники'),
        ('potionsmakers', 'Зельевары'),
        ('spellmasters', 'Мастера заклинаний'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    time_in = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    text = RichTextUploadingField(blank=True, verbose_name='Текст')
    category = models.CharField(max_length=20, choices=CATEGORY, default='tanks')

    def __str__(self):
        return f'{self.title}'

    def cat_(self):
        return self.category.field.choices[0][1]

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Response(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False, verbose_name='Статус')

    def __str__(self):
        return f'Отклик от {self.author}: {self.text}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.post.id)])


# class RegistrationCode(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     code = models.CharField(max_length=10, blank=True, null=True)




