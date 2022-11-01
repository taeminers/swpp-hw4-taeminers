from django.db import models
from django.contrib.auth.models import User
    

class Article(models.Model):
    title = models.CharField(max_length = 64)
    content = models.CharField(max_length = 1000)
    author = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name='author_set',
        default = '',
    )
    
  
class Comment(models.Model):
    content = models.TextField(max_length= 1000)
    article = models.ForeignKey(
        Article,
        on_delete= models.CASCADE,
        related_name = 'article_set',
    )
    author = models.ForeignKey(
        User,
        on_delete= models.CASCADE,
        related_name= 'user_set',
        default = '',
    )
# Create your models here.