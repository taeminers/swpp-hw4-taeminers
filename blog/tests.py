from django.test import TestCase, Client
import json
from .models import Comment, Article
from django.contrib.auth.models import User
from blog import views
from django.contrib.auth import authenticate, get_user


class BlogTestCase(TestCase):
    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection
        
    def setUp(self):
        new_user = User.objects.create_user(username = "testUsername", password = "password")
        new_user2 = User.objects.create_user(username = "swpp", password = "password")
        new_article = Article(title = 'I Love SWPP!', content = "testing", author = new_user)
        new_article.save()
        new_comment = Comment(article=new_article, content='Comment!', author=new_user)
        new_comment.save()   
        
    def test_signin(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}),
                               content_type ='application/json')
        self.assertEqual(response.status_code, 204)
        response2 = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'passsword'}),
                               content_type ='application/json')
        self.assertEqual(response2.status_code, 401)
        responseGET = client.get('/api/signin/')
        self.assertEqual(responseGET.status_code, 405)
        responseDELETE = client.delete('/api/signin/')
        self.assertEqual(responseDELETE.status_code, 405)
        responsePUT = client.put('/api/signin/')
        self.assertEqual(responsePUT.status_code, 405)
    
    def test_signup(self):
        client = Client()
        responseGET = client.get('/api/signup/')
        self.assertEqual(responseGET.status_code, 405)
        responseDELETE = client.delete('/api/signup/')
        self.assertEqual(responseDELETE.status_code, 405)
        responsePUT = client.put('/api/signup/')
        self.assertEqual(responsePUT.status_code, 405)
    
    def test_signout(self):
        client  = Client()
        responses = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}),
                               content_type ='application/json')
        responseDELETE = client.delete('/api/signout/')
        self.assertEqual(responseDELETE.status_code, 405)
        responsePUT = client.put('/api/signout/')
        self.assertEqual(responsePUT.status_code, 405)
        responsePOST = client.post('/api/signout/')
        self.assertEqual(responsePOST.status_code, 405)
        response = client.get('/api/signout/')
        self.assertEqual(response.status_code, 204)
        client.get('/api/signout/') 
        response = client.get('/api/signout/')
        self.assertEqual(response.status_code, 401)
                     
    def test_comment(self):
        client = Client()
        loggingin = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}),
                               content_type ='application/json')
        response = client.post('/api/comment/1/')
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/comment/1/')
        jsonResponse = response.json()
        self.assertEqual(response.status_code, 200)
        response3 = client.put('/api/comment/1/', json.dumps({'content': 'wow'}), content_type = 'application/json')
        self.assertEqual(response3.status_code, 200)
        response = client.put('/api/comment/1/', json.dumps({'wrongcontent': 'wow'}), content_type = 'application/json' )
        self.assertEqual(response.status_code , 400)
        responseDelete = client.delete('/api/comment/1/')
        self.assertEqual(responseDelete.status_code , 200)
        new_article = Article(title = 'I Love SWPP!', content = "testing", author = get_user(client))
        new_article.save()
        new_comment = Comment(article=new_article, content='Comment!', author=get_user(client))
        new_comment.save()   
        signout = client.get('/api/signout/')
        client.get('/api/signout/')
        response = client.get('/api/comment/1/')
        self.assertEqual(response.status_code, 401) 
        changeUser = client.post('/api/signin/', json.dumps({'username' : 'swpp', 'password': 'password'}),
                               content_type ='application/json')
        responsed = client.put('/api/comment/2/', json.dumps({'content': 'wow'}), content_type = 'application/json')
        self.assertEqual(responsed.status_code, 403)
        responseDelete = client.delete('/api/comment/2/')
        self.assertEqual(responseDelete.status_code, 403)
        lastresponse = client.get('/api/comment/1/')
        self.assertEqual(lastresponse.status_code, 404)
    
    def test_article_id(self):
        client = Client()
        loggingin = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}),
                            content_type ='application/json')
        response = client.post('/api/article/1/')
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/article/1/')
        jsonResponse = response.json()
        self.assertEqual(response.status_code, 200)
        response3 = client.put('/api/article/1/', json.dumps({'title' : 'changed' , 'content': 'wow'}), content_type = 'application/json')
        self.assertEqual(response3.status_code, 200)
        response3 = client.put('/api/article/1/', json.dumps({'wrongformat' : 'changed' , 'content': 'wow'}), content_type = 'application/json')
        self.assertEqual(response3.status_code, 400)
        responseDelete = client.delete('/api/article/1/')
        self.assertEqual(responseDelete.status_code , 200)
        new_article = Article(title = 'I Love SWPP!', content = "testing", author = get_user(client))
        new_article.save()
        signout = client.get('/api/signout/')
        response = client.get('/api/article/1/')
        self.assertEqual(response.status_code, 401)
        changeUser = client.post('/api/signin/', json.dumps({'username' : 'swpp', 'password': 'password'}),
                            content_type ='application/json')
        responsed = client.put('/api/article/2/', json.dumps({'title':'changed', 'content': 'wow'}), content_type = 'application/json')
        self.assertEqual(responsed.status_code, 403)
        responseDelete = client.delete('/api/article/2/')
        self.assertEqual(responseDelete.status_code, 403)
        lastresponse = client.get('/api/article/1/')
        self.assertEqual(lastresponse.status_code, 404)
        
    def test_article_comment(self):
        client = Client()
        loggingin = client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}), content_type ='application/json')     
        response = client.delete('/api/article/1/comment/')
        self.assertEqual(response.status_code , 405)
        response = client.put('/api/article/1/comment/')
        self.assertEqual(response.status_code , 405)
        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/article/2/comment/')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/article/1/comment/', json.dumps({'content' : 'test'}), content_type = 'application/json')
        self.assertEqual(response.status_code, 201)
        response = client.post('/api/article/1/comment/', json.dumps({'wrongconte' : 'test'}), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        signout = client.get('/api/signout/')
        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 401)
            
    def test_article(self):
        client = Client()
        client.post('/api/signin/', json.dumps({'username' : 'testUsername', 'password': 'password'}), content_type ='application/json')     
        response = client.delete('/api/article/')
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 200)
        Article.objects.filter(id = 1).delete()
        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/article/', json.dumps({'title':'title', 'content':'contenet'}), content_type = 'application/json')
        self.assertEqual(response.status_code, 201)
        response = client.post('/api/article/', json.dumps({'wrong':'title', 'content':'contenet'}), content_type = 'application/json')
        self.assertEqual(response.status_code, 400)
        signout = client.get('/api/signout/')
        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 401)
    
 