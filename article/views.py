# 引入markdown
import markdown
# 引入redirect
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse
# 引入定义的 model模型
from .models import ArticlePost
# 引入定义ArticlePostForm 表单类
from .forms import ArticlePostFrom
# 引入User模型
from django.contrib.auth.models import User
# 检查作者
from django.contrib.auth.decorators import login_required
# 支持分页
from django.core.paginator import Paginator
# 搜索
from django.db.models import Q

from comment.models import Comment
from .models import ArticleColumn
from comment.forms import CommentForm

from django.views import View
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView


# 写文章的视图
@login_required(login_url='/user/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        article_post_form = ArticlePostFrom(data=request.POST)
        # 判断提交的表单是否符合模型的要求
        if article_post_form.is_valid():
            # 保存数据但是不要提交到数据库中
            new_article = article_post_form.save(commit=False)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 指定数据库中 id=1的用户为作者
            # 如果删除数据表,可能找不到id=1 的用户
            # 需要创建用户，传入id
            new_article.author = User.objects.get(id=request.user.id)
            # 将新文章保存到数据库中
            new_article.save()
            article_post_form.save_m2m()
            # 返回文章列表
            return redirect("article:article_list")
        # 如果返回的数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果数据不合法，返回错误信息
    else:
        # 创建表单实例
        article_post_form = ArticlePostFrom()
        # 赋值上下文
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)


# 定义文章列表页面

def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章对象
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    # 将文章渲染成Markdown格式
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',  # markdown格式
            'markdown.extensions.codehilite',  # 代码高亮
            'markdown.extensions.toc'  # 目录
        ])
    # 给出模板对象
    article.body = md.convert(article.body)
    comment_form = CommentForm()
    context = {'article': article, 'toc': md.toc, 'comments': comments}
    return render(request, 'article/detail.html', context)


def article_safe_delete(request, id):
    if request.method == "POST":
        # 根据id选择删除的文章
        article = ArticlePost.objects.get(id=id)
        # 调用article的delete函数
        article.delete()
        # 完成删除后返回文章列表
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 文章的修改
@login_required(login_url='/user/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == "POST":
        # 将提交的表单存入数据库
        article_post_form = ArticlePostFrom(data=request.POST)
        # 判断提交的表单是否符合模型的要求
        if article_post_form.is_valid():
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            article.title = request.POST['title']
            article.body = request.POST['body']
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            # 返回文章列表
            return redirect("article:article_detail", id=id)
        # 如果返回的数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        # 创建表单实体
        article_post_form = ArticlePostFrom()
        # 创建上下文，将之前的article文章对象传到文本框中
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
        }
        # 返回对象render对象
        return render(request, 'article/update.html', context)


class ArticleCreateView(CreateView):
    model = ArticlePost
    fields = '__all__'
    # 或者只填写部分字段，比如：
    # fields = ['title', 'content']
    template_name = 'article/create_by_class_view.html'


class ContextMixin:
    """
    Mixin
    """
    def get_context_data(self, **kwargs):
        # 获取原有的上下文
        context = super().get_context_data(**kwargs)
        # 增加新上下文
        context['order'] = 'total_views'
        return context


class ArticleListView(ContextMixin, ListView):
    """
    文章列表类视图
    """
    # 查询集的名称
    context_object_name = 'articles'
    # 模板
    template_name = 'article/list.html'

    def get_queryset(self):
        """
        查询集
        """
        queryset = ArticlePost.objects.filter(title='Python')
        return queryset


class ArticleDetailView(DetailView):
    """
    文章详情类视图
    """
    queryset = ArticlePost.objects.all()
    context_object_name = 'article'
    template_name = 'article/detail.html'

    def get_object(self):
        """
        获取需要展示的对象
        """
        # 首先调用父类的方法
        obj = super(ArticleDetailView, self).get_object()
        # 浏览量 +1
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        return obj


class ArticleCreateView(CreateView):
    """
    创建文章的类视图
    """
    model = ArticlePost
    fields = '__all__'
    # 或者有选择的提交字段，比如：
    # fields = ['title']
    template_name = 'article/create_by_class_view.html'
