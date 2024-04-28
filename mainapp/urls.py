from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostEdit, PostDelete, \
    ResponseCreate, ResponseEdit, ResponseDelete, ResponseList

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit', PostEdit.as_view(), name='post_edit'),
    path('<int:pk>/delete', PostDelete.as_view(), name='post_delete'),
    path('responses', ResponseList.as_view(), name='response_list'),
    path('<int:pk>/response', ResponseCreate.as_view(), name='response_create'),
    path('responses/<int:pk>/edit', ResponseEdit.as_view(), name='response_edit'),
    path('responses/<int:pk>/delete', ResponseDelete.as_view(), name='response_delete'),
    ]
