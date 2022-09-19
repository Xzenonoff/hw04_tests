from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User
from .utils import paginate

NUMBER_OF_POSTS = 10


def index(request):
    post_list = Post.objects.select_related('group', 'author')
    page_obj = paginate(request, post_list, NUMBER_OF_POSTS)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group')
    page_obj = paginate(request, post_list, NUMBER_OF_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj,
        'is_group_list': True,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_post = author.posts.select_related('author')
    page_obj = paginate(request, author_post, NUMBER_OF_POSTS)
    num_of_posts = author_post.count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'num_of_posts': num_of_posts,
        'is_profile': True,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    num_of_posts = post.author.posts.count()
    context = {
        'post': post,
        'num_of_posts': num_of_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if not form.is_valid() or request.method != "POST":
        context = {
            'form': form,
        }
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:profile', request.user.username)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if not form.is_valid() or request.method != "POST":
        context = {
            'post': post,
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/create_post.html', context)

    form.save()
    return redirect('posts:post_detail', str(post_id))
