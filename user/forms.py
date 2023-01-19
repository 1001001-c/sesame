# 引入表单类
from django import forms
# 引入User数据模型
from django.contrib.auth.models import User
# 引入profile模型
from .models import Profile


# 注册表单
class UserRegisterForm(forms.ModelForm):
    # 复写user的密码
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email')

    # 对两次输入的密码是否一致进行检查
    def clean_password2(self):
        data = self.cleaned_data
        # 测试密码一致性
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            # print("密码不一致")
            raise forms.ValidationError("密码输入不一致，请重试。")


# 登录表单继承了forms.From类
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')
