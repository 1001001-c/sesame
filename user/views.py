from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileForm
from .models import Profile


# Create your views here.

@login_required(login_url='/user/register')
def user_delete(request, id):
    if request.method == "POST":
        user = User.objects.get(id=id)
        if request.user == user:
            logout(request)
            user.delete()
            return redirect('article:article_list')
        else:
            return HttpResponse("没有删除权限")
    else:
        return HttpResponse("仅接受POST请求")


# 用户注册
def user_register(request):
    # print(0)
    if request.method == "POST":
        # print(1)
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            print(user_register_form.is_valid())
            new_user = user_register_form.save(commit=False)
            # 设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            # 保存好数据后立即登录并返回博客列表
            login(request, new_user)
            # print(2)
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单输入有误请重新输入~")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'user/register.html', context)
    else:
        return HttpResponse("请使用get或POST请求数据")


# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 用户登录
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是是否匹配数据库中的某个用户
            # 如果匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户的状态保存在session中，实现了登录动作
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码错误，请重新输入~")
        else:
            return HttpResponse("账号密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {
            'form': user_login_form
        }
        return render(request, 'user/login.html', context)
    else:
        return HttpResponse("请使用post或者get方法请求数据")


# 编辑用户信息
@login_required(login_url='/user/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 onetoonefield 自动生成的字段
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者是否是本人
        if request.user != user:
            return HttpResponse("你不能修改别人的数据")

        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect
            print(id)
            return redirect('user:edit', id=id)
        else:
            return HttpResponse("输入有误请返回")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'user/edit.html', context)
    else:
        return HttpResponse("请使用get或者post请求")
