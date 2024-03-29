from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
from django.urls import reverse


# Create your models here.
# 栏目
class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


# 博客文章数据类型
class ArticlePost(models.Model):
    # 文章作者 参数 on_delete 用于指定数据的删除方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章标题 models.CharField 是字符串字段，用于保存比较短的字符串，例如标题
    title = models.CharField(max_length=100)

    # 文章正文、保存大量文本使用TextField
    body = models.TextField()

    # 文章创建时间 参数 default=timezone.now 指定其在创建时默认写入当前时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间 参数auto_now=True
    updated = models.DateTimeField(auto_now=True)
    # 文章浏览量
    total_views = models.PositiveIntegerField(default=0)
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    # 文章标签
    tags = TaggableManager(blank=True)

    # 内部类 Meta 用于给model 定义元数据
    class Meta:
        # ordering 指定模型返回数据的排列顺序
        # ‘-created' 表示按创建时间倒序排列
        ordering = ('-created',)

    # 函数 __str__(self): 定义 调用当前对象的 str() 方法时的返回值内容
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])
