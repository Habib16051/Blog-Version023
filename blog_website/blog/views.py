from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from . forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
# Class Based post view


# class PostListView(ListView):
#     # queryset = Post.published.all()
#     model = Post  # Alternatively we can use this instead of queryset! I hope you got t
#     context_object_name = 'posts'
#     paginate_by = 4
#     template_name = 'blog/home.html'


# Post List View for viewing all the post together
# # Function Based post list view

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Paginatation with 4 posts per page
    paginator = Paginator(post_list, 4)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.get_page(page_number)

    except PageNotAnInteger:
        # If a page is not an integer deliver the first page
        posts = paginator.get_page(1)

    except EmptyPage as e:
        # if a page_number is out of range deliver the lage page of results
        posts = paginator.get_page(paginator.num_pages)

    return render(request, 'blog/home.html', {'posts': posts, 'tag': tag})

# Post detail to view each single post details specifically


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post, publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comment for this post
    comments = post.comments.filter(active=True)  # type: ignore
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)  # type: ignore
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]

    # type: ignore
    # type: ignore
    return render(request, 'blog/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


# according to EmailPostForm forms.py, we need to create a view to handle the instance
# of the form and handle form submission

def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                f"{post.title}"

            comments = cd.get('comments', '')
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'habibmhr143@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post, 'form': form, 'sent': sent})


# Comment Form View

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(request.POST)  # type: ignore
    if form.is_valid():
        # Create a comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the current post to the comment
        comment.post = post
        # Save the comment tot he database
        comment.save()

    return render(request, 'blog/comment.html', {'post': post, 'form': form, 'comment': comment})


# Search View
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector(
                'title', weight='A') + SearchVector('content', weight='B')
            search_query = SearchQuery(query, config='spanish')
            results = Post.published.annotate(similiarity=TrigramSimilarity(
                'title', 'query')).filter(similarity__gt=0.1).order_by('-rank')

    return render(request, 'blog/search.html', {'form': form, 'query': query, 'results': results})
