from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from . forms import CreateTopicForm, CreatePostForm, EditPostForm
from .models import ForumPost, ForumTopic
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.

def forum_topic_list(request):
    topics = ForumTopic.objects.all().order_by('-created_at')
    context = {'topics': topics}
    return render(request, 'forum/forum_topic_list.html', context)


@login_required
def create_topic(request):
    if request.method == 'POST':
        form = CreateTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.creator = request.user
            topic.save()

            return redirect('forum:forum_topic_detail', topic_id=topic.id)
    else:
        form = CreateTopicForm()

    context = {'form': form}
    return render(request, 'forum/create_topic.html', context)


def forum_topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    posts =topic.posts.all().order_by('created_at')
    post_form = CreatePostForm()
    context = {
        'topic': topic,
        'posts': posts,
        'post_form': post_form
    }
    return render(request, 'forum/forum_topic_detail.html', context)


@login_required
def create_post(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            topic.save()

            return redirect('forum:forum_topic_detail', topic_id=topic_id)
    else:
        form = CreatePostForm()

    context = {'topic': topic, 'post_form': form}
    return render(request, 'forum/forum_topic_detail.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()

            messages.success(request, 'Post updated successfully.')
            return redirect('forum:forum_topic_detail', topic_id=post.topic.id)
    else:
        form = EditPostForm(instance=post)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'forum/edit_post.html', context)


def user_is_author_or_staff(user, post):
    return user == post.author or user.is_staff


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if not user_is_author_or_staff(request.user, post):
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect("forum:forum_topic_detail", topic_id=post.topic.id)
    
    if request.method == 'POST':
        topic_id = post.topic.id
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('forum:forum_topic_detail', topic_id=topic_id)
    else:
        context = {'post': post}
        return render(request, 'forum/delete_post_confirm.html', context)


# Implementing A search in the topic_list page.
def forum_search(request):
    search_term = request.GET.get('q')
    topics = ForumTopic.objects.all().order_by('-last_active')
    if search_term:
        topics = topics.filter(Q
        (title__icontains=search_term) |
        Q(posts__content__icontains=search_term)).distinct()

    context = {'topics': topics, 'search_term': search_term}
    return render(request, 'forum/forum_topic_list.html', context)        

