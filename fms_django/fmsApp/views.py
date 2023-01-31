from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from fms_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from fmsApp.forms import UserRegistration, SavePost, UpdateProfile, UpdatePasswords, FolderForm
from fmsApp.models import Post, Folder
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from django.contrib.auth.admin import UserAdmin

# Create your views here.

context = {
    'page_title': 'File Management System',
    'absolute_uri': '127.0.0.1:9999'
}


# login
def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')


# Logout
def logoutuser(request):
    logout(request)
    return redirect('/')


@login_required
def home(request):
    context['page_title'] = 'Home'
    context['on_page'] = True
    folders = Folder.objects.filter(on_page=True).all()
    posts = Post.objects.filter(on_page=True).all()

    context['posts'] = posts
    context['folders'] = folders
    context['postsLen'] = posts.count() + folders.count()
    print(request.build_absolute_uri())
    print(context)
    return render(request, 'home.html', context)


def user_files(request, pk):
    context['on_page'] = False
    account = User.objects.get(id=pk)
    folders = Folder.objects.filter(user=account, folder=None).all()
    posts = Post.objects.filter(user=account, folder=None).all()
    print(context)
    context['account'] = account
    context['posts'] = posts
    context['folders'] = folders
    context['postsLen'] = posts.count() + folders.count()
    context['page_title'] = account.username
    context['folder_in'] = None
    print(request.build_absolute_uri())
    return render(request, 'home.html', context)


def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username=username, password=pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request, 'register.html', context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html', context)


@login_required
def posts_mgt(request):
    context['page_title'] = 'Uploads'

    posts = Post.objects.filter(user=request.user).order_by('title', '-date_created').all()
    context['posts'] = posts
    return render(request, 'posts_mgt.html', context)


@login_required
def manage_post(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    print(pk)
    if not pk is None:
        post = Post.objects.get(id=pk)
        context['post'] = post
    return render(request, 'manage_post.html', context)


@login_required
def manage_post_folder(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    print(context)
    print(pk)
    if pk:
        folder = Folder.objects.get(id=pk)
        context['folder_in'] = folder
    return render(request, 'manage_post.html', context)


@login_required
def manage_folder(request, pk=None):
    print(pk)
    context['page_title'] = 'Manage Post'
    context['folder'] = {}
    if pk:
        folder = Folder.objects.get(id=pk)
        context['folder_in'] = folder
    return render(request, 'manage_folder.html', context)


@login_required
def save_post(request, pk=None):
    print(context)
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if not request.POST['id'] == '':
            post = Post.objects.get(id=request.POST['id'])
            form = SavePost(request.POST, request.FILES, instance=post)
        else:
            form = SavePost(request.POST, request.FILES)
        if form.is_valid():
            print('valid')
            if pk:
                print('da')
                das = form.save(commit=False)
                if context['on_page'] == True:
                    das.on_page = True
                else:
                    das.on_page = False
                    das.user = request.user
                das.folder = Folder.objects.get(id=pk)
                das.save()
            else:

                das = form.save(commit=False)

                if context['on_page']:
                    das.on_page = True
                else:
                    das.on_page = False
                    print('сработало')
                    das.user = request.user
                das.on_page = True
                print(das.user)
                das.user = None
                das.save()
            messages.success(request, 'File has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + '<br/>')
            form = SavePost(request.POST, request.FILES)

    else:
        resp['msg'] = "No Data sent."
    print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def save_folder(request, pk=None):
    print(pk)
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if not request.POST['id'] == '':
            folder = Folder.objects.get(id=request.POST['id'])
            form = FolderForm(request.POST, instance=folder)
        else:
            form = FolderForm(request.POST)
        if form.is_valid():
            if not pk is None:
                das = form.save(commit=False)
                das.user = request.user
                das.public = False
                das.folder = Folder.objects.get(id=pk)
                das.save()
                messages.success(request, 'File has been saved successfully.')
                resp['status'] = 'success'
            else:
                das = form.save(commit=False)
                das.public = True
                if context['on_page'] == True:
                    das.on_page = True
                else:
                    das.on_page = False
                    print('сработал')
                    das.user = request.user
                das.save()
                messages.success(request, 'File has been saved successfully.')
                resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + '<br/>')
            form = FolderForm(request.POST)

    else:
        resp['msg'] = "No Data sent."
    print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_post(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=request.POST['id'])
            post.delete()
            resp['status'] = 'success'
            messages.success(request, 'Post has been deleted successfully')
        except:
            resp['msg'] = "Undefined Post ID"
    return HttpResponse(json.dumps(resp), content_type="application/json")


def shareF(request, id=None):
    # print(str("b'UdhnfelTxqj3q6BbPe7H86sfQnboSBzb0irm2atoFUw='").encode())
    context['page_title'] = 'Shared File'
    if not id is None:
        key = settings.ID_ENCRYPTION_KEY
        fernet = Fernet(key)
        id = base64.urlsafe_b64decode(id)
        id = fernet.decrypt(id).decode()
        post = Post.objects.get(id=id)
        context['post'] = post
        context['page_title'] += str(" - " + post.title)

    return render(request, 'share-file.html', context)


@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form

    return render(request, 'manage_profile.html', context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request, 'update_password.html', context)


@login_required
def folder_detail(request, pk):
    context['on_page'] = False
    context['page_title'] = 'Папка'
    folders = Folder.objects.filter(folder=pk).all()
    if request.user.is_superuser:
        posts = Post.objects.filter(folder=pk).all()

    else:
        posts = Post.objects.filter(folder=pk).all()
    folder = Folder.objects.get(id=pk)
    context['folder'] = folder
    context['page_title'] = folder.title
    context['posts'] = posts
    context['postsLen'] = posts.count()
    context['folders'] = folders
    print(request.build_absolute_uri())
    return render(request, 'folder_detail.html', context)


@login_required
def user_list(request):
    users = User.objects.all()
    context['users'] = users
    return render(request, 'user_list.html', context)