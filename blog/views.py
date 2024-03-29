from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from json.decoder import JSONDecodeError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Article, Comment
from django.contrib.auth import authenticate, login, logout


def signup(request):
    """if request.method == 'GET' or request.method =='DELETE' or request.method == 'PUT':
        return HttpResponse(status = 405)"""
    if request.method == 'POST':
        #do we need to check if username already exsits?
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
    else : 
        return HttpResponse(status=405)
    
def signin(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        theUser = authenticate(username = username, password= password)
        if theUser is not None:
            login(request, theUser)
            return HttpResponse(status = 204)
        else:
            return HttpResponse(status=401)
    else :
        return HttpResponse(status = 405)  
    
def signout(request):
    """if request.method == 'DELETE' or request.method == 'PUT' or request.method == 'POST':
        return HttpResponse(status=405)"""
    if request.method == 'GET':
        if request.user.is_authenticated :
            logout(request)
            return HttpResponse(status = 204)
        else :
            return HttpResponse(status = 401)
    else : 
        return HttpResponse(status=405)

    
        
def comment(request, id):
    if request.method == 'GET':
        if request.user.is_authenticated :
            if (Comment.objects.filter(id = id)): 
                comment = Comment.objects.get(id = id)
                response_comment = {'article' : comment.article_id , 'content' : comment.content, 'author' : comment.author_id}
                return JsonResponse(response_comment)
            else:
                return HttpResponse(status= 404)
        else:
            return HttpResponse(status = 401)
    elif request.method == 'PUT':
        if request.user.is_authenticated :
            if (Comment.objects.filter(id = id)): 
                comment = Comment.objects.get(id = id)
                try : 
                    body = request.body.decode()
                    comment_content = json.loads(body)['content']
                except (KeyError, JSONDecodeError) as e:
                    return HttpResponseBadRequest()
                if (comment.author_id == request.user.id):
                    comment.content = comment_content
                    comment.save()
                    response_comment = {"id" : comment.id, "content" : comment.content, "author_id" : comment.author_id, "article_id" : comment.article_id}
                    return HttpResponse(json.dumps(response_comment), content_type = "application/json", status=200)
                else :
                    return HttpResponse(status = 403)
            else :
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=401)
    elif request.method == 'DELETE':
        if request.user.is_authenticated :
            if (Comment.objects.filter(id = id)): 
                comment = Comment.objects.get(id = id)
                if (comment.author_id == request.user.id):
                    Comment.objects.filter(id = id).delete()
                    return HttpResponse(status = 200)
                else :
                    return HttpResponse(status=403)
            else:
                return HttpResponse(status=404)
        else :
            return HttpResponse(status = 401)
    else :
        return HttpResponse(status=405)
        

def article_id(request, id):
    if request.method == 'GET':
        if request.user.is_authenticated :
            if (Article.objects.filter(id = id)):
                article = Article.objects.get(id = id)
                response_article = {'title': article.title, 'content' : article.content, 'author' : article.author_id}
                return JsonResponse(response_article)
            else :
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=401)
    elif request.method == 'PUT':
        if request.user.is_authenticated :
            if (Article.objects.filter(id = id)):
                article = Article.objects.get(id = id)
                try :
                    body  = request.body.decode()
                    article_title = json.loads(body)['title']
                    article_content = json.loads(body)['content']
                except (KeyError, JSONDecodeError) as e:
                    return HttpResponseBadRequest()
                if (article.author_id == request.user.id):
                    article.title = article_title
                    article.content = article_content
                    article.save()
                    response_article = {"title": article.title, "content": article.content, "id" : article.id}
                    return HttpResponse(json.dumps(response_article), content_type= "application/json", status=200)
                else :
                    return HttpResponse(status=403)
            else :
                return HttpResponse(status=404)
        else :
            return HttpResponse(status=401)
    elif request.method == 'DELETE':
        if request.user.is_authenticated :
            if (Article.objects.filter(id = id)):
                article = Article.objects.get(id = id)
                if(article.author_id == request.user.id):
                    Article.objects.filter(id = id).delete()
                    return HttpResponse(status = 200)
                else :
                    return HttpResponse(status = 403)
            else :
                return HttpResponse(status=404)
        else :
            return HttpResponse(status = 401)
    else :
        return HttpResponse(status=405)
        
def article_comment(request, id):   
    if request.method == 'GET':
        if request.user.is_authenticated :
            #test this again
            comments = [comment for comment in Comment.objects.filter(article_id = id).values()]
            if (comments):
                for comment in comments:
                    comment.pop("id")
                return JsonResponse(comments, safe = False)
            else :
                return HttpResponse(status=404)
        else :
            return HttpResponse(status = 401)
    elif request.method == 'POST':
        if request.user.is_authenticated :
            try :
                body = request.body.decode()
                comment_content = json.loads(body)['content']
            except (KeyError, JSONDecodeError) as e:
                return HttpResponseBadRequest()
            newComment = Comment(content = comment_content, article_id = id , author = request.user)
            newComment.save()
            response_comment = {'content' : newComment.content, "id" : newComment.id, "author_id" : newComment.author_id, "article_id" : newComment.article_id}
            return HttpResponse(json.dumps(response_comment), content_type = "application/json", status = 201)
        else :
            return HttpResponse(status=401)
    else :
        return HttpResponse(status=405)
    
def article(request):
    if request.method == 'GET':
        if request.user.is_authenticated :
            if(Article.objects.all()):
                article_set = [article for article in Article.objects.all().values()]
                for article in article_set:
                    article.pop("id")
                return JsonResponse(article_set, safe = False)    
            else :
                return HttpResponse(status =404)
        else :
            return HttpResponse(status = 401)
    elif request.method == 'POST':
        if request.user.is_authenticated :
            try :
                body = request.body.decode()
                article_title = json.loads(body)['title']   
                article_content = json.loads(body)['content'] 
                article_user = request.user
            except (KeyError, JSONDecodeError) as e :
                return HttpResponseBadRequest()
            article = Article(title = article_title, content = article_content, author = article_user)
            article.save()
            response_article = {'title' : article.title, 'content' : article.content, 'id' : article.id, 'author_id' : article.author_id}
            return HttpResponse(json.dumps(response_article), content_type = "application/json", status=201)
        else : 
            return HttpResponse(status = 401)
    else :
        return HttpResponse(status = 405)
    
@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
