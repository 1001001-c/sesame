"""
@author lzq
article/forms.py
"""
# 引入表单类
from django import forms
# 引入文章模型
from .models import ArticlePost

# 写文章的表单
class ArticlePostFrom(forms.ModelForm):
    class Meta:
        # 指明数据来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'tags')
