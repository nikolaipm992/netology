from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from .models import Article, Tag, Scope


class ScopeInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        main_scopes_count = 0
        
        # Проверяем, есть ли данные
        if any(self.errors):
            return
            
        # Считаем основные теги и проверяем дубликаты
        tags_list = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                is_main = form.cleaned_data.get('is_main', False)
                tag = form.cleaned_data.get('tag')
                
                if tag:
                    if tag in tags_list:
                        raise ValidationError('Один и тот же тег не может быть выбран дважды для одной статьи.')
                    tags_list.append(tag)
                    
                    if is_main:
                        main_scopes_count += 1
        
        # Проверка количества основных тегов
        if main_scopes_count == 0 and tags_list:
            raise ValidationError('Должен быть указан ровно один основной раздел.')
        elif main_scopes_count > 1:
            raise ValidationError('Может быть только один основной раздел.')


class ScopeInline(admin.TabularInline):
    model = Scope
    formset = ScopeInlineFormset
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at']
    inlines = [ScopeInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']