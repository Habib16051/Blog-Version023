
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from . forms import EmailPostForm
# Class Based post view


class PostListView(ListView):
    # queryset = Post.published.all()
    model = Post  # Alternatively we can use this instead of queryset! I hope you got t
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'blog/home.html'


# Post List View for viewing all the post together
# # Function Based post list view

# def post_list(request):
#     post_list = Post.published.all()

#     # Paginatation with 3 posts per page
#     paginator = Paginator(post_list, 4)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.get_page(page_number)

#     except PageNotAnInteger:
#         posts = paginator.get_page(1) # If a page is not an integer deliver the first page

#     except EmptyPage as e:
#         posts = paginator.get_page(paginator.num_pages) # if a page_number is out of range deliver the lage page of results


#     return render(request, 'blog/home.html', {'posts': posts})

# Post detail to view each single post details specifically
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post, publish__year=year,
                             publish__month=month,
                             publish__day=day)

    return render(request, 'blog/detail.html', {'post': post})  # type: ignore


# according to EmailPostForm forms.py, we need to create a view to handle the instance
# of the form and handle form submission

def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data['email']

    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post, 'form': form})
