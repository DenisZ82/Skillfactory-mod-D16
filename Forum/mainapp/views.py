from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from Forum import settings
from .models import Post, Response, User
from .filters import PostFilter, PrivateFilter
from .forms import PostForm, ResponseForm


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset

        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('mainapp.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            post.author = self.request.user
        post.save()
        return super().form_valid(form)


class PostEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('mainapp.change_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('Изменения доступны только автору')

    # def has_permission(self):
    #     has_perms = super().has_permission()
    #     self.object = self.get_object()
    #     user_is_author = self.object.author == self.request.user
    #     return user_is_author


class PostDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('mainapp.delete_post',)
    raise_exception = True
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('Удаление доступно только автору')

    # def has_permission(self):
    #     has_perms = super().has_permission()
    #     self.object = self.get_object()
    #     user_is_author = self.object.author == self.request.user
    #     return has_perms or user_is_author


class ResponseCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('mainapp.add_response',)
    raise_exception = True
    form_class = ResponseForm
    model = Response
    template_name = 'response_edit.html'

    def form_valid(self, form):
        response = form.save(commit=False)
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        if self.request.method == 'POST':
            response.author = self.request.user
            response.post_id = self.kwargs.get('pk')
        response.save()
        send_mail(
            subject=f'Отклик на объявление {post}',
            message=f'На объявление {post} был добавлен отклик пользователем {self.request.user}: {response.text}. '
                    f'Ссылка на объявление: http://127.0.0.1:8000/posts/{response.post.id}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[User.objects.get(pk=post.author_id).email]
        )
        return super().form_valid(form)


class ResponseEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('mainapp.change_response',)
    raise_exception = True
    form_class = ResponseForm
    model = Response
    template_name = 'response_edit.html'

    def dispatch(self, request, *args, **kwargs):
        author = Response.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('Изменения доступны только автору')


class ResponseDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('mainapp.delete_response',)
    raise_exception = True
    model = Response
    template_name = 'response_delete.html'

    # для возврата к странице объявления, где был удален отклик
    def get_success_url(self):
        return reverse_lazy('post_detail', args=[self.object.post_id])

    # для проверки залогиненого пользователя на авторство отклика
    def dispatch(self, request, *args, **kwargs):
        author = Response.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('Удаление доступно только автору')


class ResponseList(LoginRequiredMixin, ListView):
    template_name = 'private.html'
    model = Response
    ordering = '-time_in'
    context_object_name = 'responses'

    def get_queryset(self):
        queryset = Response.objects.filter(post__author_id=self.request.user.id)
        self.filterset = PrivateFilter(self.request.GET, queryset, request=self.request.user.id)
        if self.request.GET:
            return self.filterset.qs
        return Response.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


@login_required
@csrf_protect
def accept_reject(request, **kwargs):
    if request.method == 'POST':
        # response_id = request.POST.get('response_id')
        response = Response.objects.get(id=kwargs.get('pk'))
        action = request.POST.get('action')
        post = get_object_or_404(Post, id=response.post.id)

        if action == 'accept':
            response.status = True
            response.save()
            send_mail(
                subject=f'Отклик принят',
                message=f'Отклик на объявление {post} принят: {response.text}. '
                        f'Ссылка на объявление: http://127.0.0.1:8000/posts/{response.post.id}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[User.objects.get(pk=response.author_id).email]
            )

        elif action == 'reject':
            response.status = False
            response.save()
            send_mail(
                subject=f'Отклик отклонен',
                message=f'Отклик на объявление {post} отклонен: {response.text}. '
                        f'Ссылка на объявление: http://127.0.0.1:8000/posts/{response.post.id}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[User.objects.get(pk=response.author_id).email]
            )

    return redirect('post_detail', response.post_id)


class ConfirmUser(UpdateView):
    model = User
    context_object_name = 'confirm_user'

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = User.objects.filter(code=request.POST['code'])
            if user.exists():
                user.update(is_active=True)
                user.update(code=None)
            else:
                return render(self.request, 'invalid_code.html')

        return redirect('account_login')
