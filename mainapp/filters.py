import django_filters
from django_filters import FilterSet, DateTimeFilter, ModelMultipleChoiceFilter, ChoiceFilter, ModelChoiceFilter
from django.forms import DateTimeInput


from .models import Post, User, Response

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


class PostFilter(FilterSet):
    """ Filtering ads on the '/posts' page"""
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок',
    )

    added_after = DateTimeFilter(
        label='Дата публикации после',
        field_name='time_in',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    category = ChoiceFilter(
        choices=CATEGORY,
        field_name='category',
        label='Категория',
    )

    author = ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ['category', 'author']


class PrivateFilter(FilterSet):

    class Meta:
        model = Response
        fields = [
            'post',
        ]

    def __init__(self, *args, **kwargs):
        super(PrivateFilter, self).__init__(*args, **kwargs)
        self.filters['post'].queryset = Post.objects.filter(author_id=kwargs['request'])

