# python
# django
# api
# apps
import sendgrid
from sendgrid.helpers.mail import *
from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel, TagModel, FetchModel
from django.contrib.auth.hashers import make_password, check_password
# for mailing through settings
# from django.core.mail import send_mail
# from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from socially.settings import BASE_DIR
from keys import YOUR_CLIENT_ID, YOUR_CLIENT_SECRET
from imgurpython import ImgurClient
from clarifai.rest import ClarifaiApp
from paralleldots import sentiment, set_api_key

from django.http import HttpResponse
from django.views.generic import View

from social.utils import render_to_pdf #created in step 4
import datetime

CLARIFAI_API_KEY = 'f3a37216201f4c3faae31795abd09ee6'
app = ClarifaiApp(api_key=CLARIFAI_API_KEY)

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import traceback

from socially.cre import SENDGRID_API_KEY

def index_view(request):
    return render(request, 'index.html')


def detail_view(request, post_id):
    user = check_validation(request)
    if user:
        post = PostModel.objects.filter(pk=post_id).first()
        existing_like = LikeModel.objects.filter(post=post.id, user=user).first()
        if existing_like:
            post.has_liked = True

        comments = CommentModel.objects.filter(post=post.id)
        pos = 0
        neg = 0
        for comment in comments:

            if comment.review == 'positive' :
                pos += 1
            else:
                neg += 1
        print pos

        if pos > neg:
            post.has_recommended = True
        else:
            post.has_recommended = False

    return render(request, 'details.html', {'post': post})


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return redirect('/social/login/')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/social/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)
                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()
                model = app.models.get('general-v1.3')  # notify model which we are going to use from clarifai
                response = model.predict_by_url(url=post.image_url)  # pass the url of current image

                if response["status"]["code"] == 10000:
                    if response["outputs"]:
                        if response["outputs"][0]["data"]:
                            if response["outputs"][0]["data"]["concepts"]:
                                concepts = response["outputs"][0]["data"]["concepts"]
                                for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                                    # for concept in concepts[:10]:
                                    tag = response["outputs"][0]["data"]["concepts"][index]['name']

                                    hash = TagModel.objects.filter(tag_text=tag)

                                    if (hash.__len__() == 0):
                                        hash = TagModel(tag_text=tag)
                                        hash.save()
                                    else:
                                        hash = hash[0]

                                    fetch = FetchModel(id_of_tag=hash, id_of_post=post)
                                    fetch.save()
                                return redirect('/social/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/social/login/')


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

            comments = CommentModel.objects.filter(post=post.id)
            pos = 0
            neg = 0
            for comment in comments:
                print comment.review

                if comment.review == "negative":
                    neg += 1
                    print "positive comment"
                elif comment.review == "positive":
                    pos += 1
            print pos


            if pos > neg:
                post.has_recommended = True
            else:
                post.has_recommended = False

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/social/login/')


# retriving images based on analysis of content
def tag_view(request):
    user = check_validation(request)
    if user:
        q = request.GET.get('q')
        hash = TagModel.objects.filter(tag_text=q).first()
        posts = FetchModel.objects.filter(id_of_tag=hash)
        posts = [post.id_of_post for post in posts]
        if (posts == []):
            return HttpResponse("<H1><CENTER>NO SUCH TAG FOUND</H1>")
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/social/login/')


def tag_view_u(request, hash_tag):
    user = check_validation(request)
    if user:

        hash = TagModel.objects.filter(tag_text=hash_tag).first()
        posts = FetchModel.objects.filter(id_of_tag=hash)
        posts = [post.id_of_post for post in posts]
        if (posts == []):
            # make a 404 page and render it
            return HttpResponse("<H1><CENTER>NO SUCH TAG FOUND</H1>")
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/social/login/')


def user_view(request):
    user = check_validation(request)

    if user:
        query = request.GET.get('q')
        user = UserModel.objects.filter(username=query).first()
        posts = PostModel.objects.filter(user=user)
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/social/login/')


def user_view_u(request, user_name):
    user = check_validation(request)

    if user:
        user = UserModel.objects.filter(username=user_name).first()
        posts = PostModel.objects.filter(user=user)
        # not_neccessary to make list
        posts = [post for post in posts]
        if posts == []:
            # make a 404 page and render it
            return HttpResponse("<h1>No such user found</h1>")
        else:
            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True
            return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/social/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            post = PostModel.objects.filter(pk=post_id)
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                post.has_liked = True
            else:
                post.has_liked = False
                existing_like.delete()

            return redirect('detail', post_id=post_id)
    else:
        return redirect('/social/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            post = PostModel.objects.filter(pk=post_id)
            comment_text = str(form.cleaned_data.get('comment_text'))
            set_api_key('qvGZYufnXUmQNxbFi6h4GDlNtu30HKzhFxJvMUnAdNc')
            review = sentiment(comment_text)

            if review['sentiment']:
                comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text,
                                                      review=review['sentiment'])
                print comment.review
                comment.save()
                return redirect('detail', post_id=post_id)
    else:
        return redirect('/social/login/')


def logout_view(request):

    response = redirect('/social/login/')
    response.delete_cookie(key='session_token')
    return response


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None

def display():
    objects = CommentModel.objects.all()

    for object in objects:
        print object.review



def threeD_view(request, post_id):
    user = check_validation(request)
    if user:
        post = PostModel.objects.filter(pk=post_id).first()

    return render(request, 'threeD.html', {'post': post})


def GeneratePdf_view(request, post_id):
    context = {
        "invoice_id": 123,
        "customer_name": "John Cooper",
        "amount": 1399.99,
        "today": "Today",
        "post_id":post_id
    }
    html = render(request, 'threeD.html', {'context': context})
    pdf = render_to_pdf('invoice.html', context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" %("12341231")
        content = "inline; filename='%s'" %(filename)
        download = True
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return html



'''


sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = Email("inderpreet726b@gmail.com")
        #to_email = Email(user.email)

        to_email = Email('ivjotofficial@gmail.com')
        subject = "lets do something bro"
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = filename_l
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path,'rb') as f:
            data = f.read()
            f.close()
        import base64
        encoded = base64.b64encode(data)

        attachment = Attachment()
        attachment.set_content(pdf)
        attachment.set_type("application/pdf")
        attachment.set_filename(filename)
        attachment.set_disposition("attachment")
        attachment.set_content(encoded)
        mail = Mail(from_email, subject, to_email, content)
        mail.add_attachment(attachment)
        content = Content("text/plain", "hackers")
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print response.status_code
        print response.body
        print response.headers

        #send_mail(subject,message,from_email,to_list,fail_silently=True)
        # subject="Thankyou for signing up"
        # message="you will enjoy our services \n we will in touch soon"
        # from_email=settings.EMAIL_HOST_USER
        # to_list =[user.email]
        # send_mail(subject,message,from_email,to_list,fail_silently=True)
        # #return render(request, 'login.html')
        
try:
    parent_folder_name = 'bills'
    try:
        import argparse
        import os
        flags = tools.argparser.parse_args(['--noauth_local_webserver'])
    except ImportError:
        flags = None
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = file.Storage(credential_path)
    credentials = store.get()
    scopes = 'https://www.googleapis.com/auth/drive.file'
    store = file.Storage('storage.json')
    credentials = None
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('social/client_secret.json', scope=scopes)
        credentials = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)
    drive = build('drive', 'v3', http=credentials.authorize(Http()))
    files = ((filename, 'application/vnd.google-apps.document'),)
    # code to create folder + if folder exist do not create new +find id

    # first look for the parent folder chats
    folder_name_context = {}
    page_token = None
    while True:
        response = drive.files().list(q="mimeType='application/vnd.google-apps.folder'", spaces='drive',
                                      fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
        for file_response in response.get('files', []):
            folder_name_context[file_response.get('name')] = file_response.get('id')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    if parent_folder_name in folder_name_context.keys():
        parent_folder_id = folder_name_context[parent_folder_name]
    else:
        file_metadata = {
            'name': parent_folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.files().create(body=file_metadata, fields='id').execute()
        folder_name_context[parent_folder_name] = folder.get('id')
        parent_folder_id = folder_name_context[parent_folder_name]

    # now look for the main folder in which chat is to be saved
    folder_name_context = {}
    page_token = None
    while True:
        response = drive.files().list(q="mimeType='application/vnd.google-apps.folder'", spaces='drive',
                                      fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
        for file_response in response.get('files', []):
            folder_name_context[file_response.get('name')] = file_response.get('id')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    folder_name='bills'
    if folder_name in folder_name_context.keys():
        folder_id = folder_name_context[folder_name]
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = drive.files().create(body=file_metadata, fields='id').execute()
        folder_name_context[folder_name] = folder.get('id')
        folder_id = folder_name_context[folder_name]

    # code to create file in a folder
    for filename, mimeType in files:
        file_metadata = {'name': filename, 'parents': [folder_id]}
        if mimeType:
            file_metadata['mimeType'] = mimeType
        file_to_upload = drive.files().create(body=file_metadata, media_body=filename, fields='id').execute()
        status = "success"
        return status
    # https://drive.google.com/open?id=1W1bYTdgrZobFfmwQy1tnCSS0cm9GXF7F
except Exception as e:
    traceback_string = traceback.format_exc()
    print str(traceback_string)
'''
