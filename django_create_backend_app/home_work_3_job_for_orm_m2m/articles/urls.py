from django.urls import path
from .views import ArticlesListView, ArticleDetailView

urlpatterns = [
    path('', ArticlesListView.as_view(), name='articles'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article'),
]