from django.shortcuts import render
from social.models import PostModel
def detail_view(request,post_id):
    post=PostModel.objects.filter(pk=post_id).first()
    return render(request,'details.html',{'post':post})