# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.contrib import admin
from social.models import UserModel,PostModel,TagModel,CommentModel,FetchModel,LikeModel

admin.site.register(UserModel)
admin.site.register(PostModel)
admin.site.register(TagModel)
admin.site.register(LikeModel)
admin.site.register(CommentModel)
admin.site.register(FetchModel)
