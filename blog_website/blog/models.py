from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# Custom Model Managers


class PublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.


class Post(models.Model):

    class Status(models.TextChoices):  # Subclass for ensurining the post is published or draft
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')  # type: ignore
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='media/images')
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    Updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT)

    # default manager
    objects = models.Manager()

    # Custom Manager
    published = PublishedManager()

    # tags manager
    tags = TaggableManager()

    class Meta:
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish']),]

    def __str__(self):
        return self.title
    # make the url more dynamically to interact with the view more fastly

    def get_absolute_url(self):
        # type: ignore
        return reverse("blog:post_detail", args=[self.publish.year, self.publish.month, self.publish.day, self.slug])


# models for handling the comment section
class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')

    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created']),]

    def __str__(self):
        return f"comment by {self.name} on {self.post}"
