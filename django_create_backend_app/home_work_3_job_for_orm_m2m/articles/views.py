from django.views.generic import ListView
from django.db import models
from django.db.models import Prefetch
from .models import Article, Scope


class ArticlesListView(ListView):
    model = Article
    template_name = 'articles/news.html'
    context_object_name = 'object_list'
    ordering = ['-published_at']

    def get_queryset(self):
        # Prefetch для оптимизации запросов и правильной сортировки
        prefetch_scopes = Prefetch(
            'scope_set',
            queryset=Scope.objects.select_related('tag').order_by(
                models.Case(
                    models.When(is_main=True, then=models.Value(0)),
                    default=models.Value(1),
                    output_field=models.IntegerField()
                ),
                'tag__name'
            )
        )
        
        return Article.objects.prefetch_related(prefetch_scopes).all()


class ArticleDetailView(ListView):
    model = Article
    template_name = 'articles/article.html'

    def get_queryset(self):
        prefetch_scopes = Prefetch(
            'scope_set',
            queryset=Scope.objects.select_related('tag').order_by(
                models.Case(
                    models.When(is_main=True, then=models.Value(0)),
                    default=models.Value(1),
                    output_field=models.IntegerField()
                ),
                'tag__name'
            )
        )
        
        return Article.objects.prefetch_related(prefetch_scopes).filter(pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object_list']:
            context['article'] = context['object_list'][0]
        return context