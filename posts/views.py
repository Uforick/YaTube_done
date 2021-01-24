from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    is_edit = False
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse('index'))
    return render(
        request,
        'posts/new.html',
        {'form': form, 'is_edit': is_edit})


def profile(request, username):
    author = User.objects.get(username=username)
    post_list_author = author.posts.all()
    count_posts = post_list_author.count()
    paginator = Paginator(post_list_author, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow_check = (
        request.user.is_authenticated and
        Follow.objects.filter(
            user=request.user,
            author=author).exists()
    )
    followers = Follow.objects.filter(user__follower__author=author).count()
    follows = Follow.objects.filter(author__following__user=author).count()

    return render(
        request,
        'posts/profile.html',
        {'page': page,
         'author': author,
         'count_posts': count_posts,
         'paginator': paginator,
         'following': follow_check,
         'follows': follows,
         'followers': followers
         }
    )


def post_view(request, username, post_id):
    post_id = Post.objects.get(
        pk=post_id, author=User.objects.get(username=username)
    )
    count_posts = post_id.author.posts.count()
    comments = post_id.comments.all()
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post.html',
        {'post': post_id,
         'author': post_id.author,
         'count_posts': count_posts,
         'comments': comments,
         'form': form}
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post, pk=post_id, author=User.objects.get(username=username)
    )
    is_edit = True
    if request.user != post.author:
        return redirect(reverse(
            'post',
            kwargs={'username': username,
                        'post_id': post_id}))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect(reverse(
            'post',
            kwargs={'username': username,
                        'post_id': post_id}))
    return render(
        request,
        'posts/new.html',
        {'form': form, 'post': post, 'is_edit': is_edit})


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(
        pk=post_id, author=User.objects.get(username=username)
    )
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect(reverse('post', kwargs={'username': username,
                                                'post_id': post_id}))
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user == author) or (Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()):
        return redirect(reverse(
            'profile',
            kwargs={'username': username}
        ))
    Follow.objects.create(
        user=request.user,
        author=author,
    )
    return redirect(reverse(
        'profile',
        kwargs={'username': username}
    ))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect(reverse(
        'profile',
        kwargs={'username': username}
    ))


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
