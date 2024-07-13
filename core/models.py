from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.dispatch import receiver
from django.conf import settings
from userauths.models import User, Profile, user_directory_path

from PIL import Image
from shortuuid.django_fields import ShortUUIDField
import shortuuid
import os

User = settings.AUTH_USER_MODEL

CATEGORY = (

    ("Technology","technology"),
    ("Cars and Vehicle","cars and vehicle"),
    ("Comedy ","comedy"),
    ("Economics and Trade ","economics and trade"),
    ("Education ","Education"),
    ("Entertainment ","entertainment"),
    ("Movies and Animation ","movies and animation"),
    ("Gaming ","gaming"),
    ("History and Facts ","history and facts"),
    ("LifeStyle","lifestyle"),
    ("Others ","others")


)

VISIBILITY = (
    ("Only Me","Only Me"),
    ("Everyone","Everyone"),
)

FRIEND_REQUEST = (
    ("pending","pending"),
    ("accept","Accept"),
    ("reject","Reject"),
)


NOTIFICATION_TYPE = (
    ("Friend Request", "Friend Request"),
    ("Friend Request Accepted", "Friend Request Accepted"),
    ("New Follower", "New Follower"),
    ("New Like", "New Like"),
    ("New Comment", "New Comment"),
    ("Comment Liked", "Comment Liked"),
    ("Comment Replied", "Comment Replied"),


)

from django.db import models
from django.contrib.auth.models import User
from shortuuidfield import ShortUUIDField
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from datetime import datetime


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.FileField(upload_to='user_directory_path', null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone",
                                  choices=[("everyone", "Everyone"), ("friends", "Friends"), ("private", "Private")])
    pid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    # Fields for live video
    is_live = models.BooleanField(default=False)
    live_meeting_url = models.URLField(max_length=500, blank=True, null=True)
    live_start_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Posts"

    def save(self, *args, **kwargs):
        uuid_key = ShortUUIDField().random(length=4)
        uniqueid = uuid_key[:4]
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(Post, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe(
            '<img src="/media/%s" width="50" height="50" object-fit="cover" style="border-radius: 5px;" />' % (
                self.image))

    def gallery_images(self):
        return Gallery.objects.filter(post=self)

    def title_len_count(self):
        return len(self.title)

    def gallery_img_count(self):
        return Gallery.objects.filter(post=self).count()

    def post_comments(self):
        return Comment.objects.filter(post=self, active=True)

    def post_comments_count(self):
        return Comment.objects.filter(post=self, active=True).count()


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    sid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="story_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Story"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(Story, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

    def gallery_images(self):
        return Gallery.objects.filter(story=self)

    def title_len_count(self):
        return len(self.title)

    def galley_img_count(self):
        return Gallery.objects.filter(story=self).count()

    def story_comments(self):
        comments = Comment.objects.filter(story=self, active=True)
        return comments

    def story_comments_count(self):
        comments_count = Comment.objects.filter(story=self, active=True).count()
        return comments_count


@receiver(models.signals.pre_delete, sender=Post)
def delete_image_file(sender, instance, **kwargs):
    # Check if the image field has a value
    if instance.image:
        # Get the path of the image file
        image_path = instance.image.path
        # Check if the image file exists
        if os.path.exists(image_path):
            # Delete the image file
            os.remove(image_path)


class Gallery(models.Model):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="gallery", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.post)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Gallery"

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 30px;" />' % (self.image))


class FriendRequest(models.Model):
    fid = ShortUUIDField(  max_length=25 )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="request_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="request_receiver")
    status = models.CharField(max_length=10, default="pending", choices=FRIEND_REQUEST)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}"

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Friend Request"

class Friend(models.Model):
    fid = ShortUUIDField(  max_length=25 )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Friend"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, blank=True ,null=True)
    date = models.DateTimeField(auto_now_add=True)
    cid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="comment_likes")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Comment"

    def comment_replies(self):
        comment_replies = ReplyComment.objects.filter(comment=self, active=True)
        return comment_replies


class ReplyComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reply = models.CharField(max_length=500, blank=True ,null=True)
    date = models.DateTimeField(auto_now_add=True)
    cid = ShortUUIDField(  max_length=25 )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Reply Comment"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="noti_user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_sender")
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_post")
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_comment")
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE, default="none")
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    nid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Notification"

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"


class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    members = models.ManyToManyField(User, blank=True, related_name="members")

    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    name = models.CharField(max_length=500, blank=True ,null=True)
    description = models.TextField(blank=True ,null=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    gid = ShortUUIDField(  max_length=25 )
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username
    #def __str__(self):
    #    return self.name

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(Group, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

    def memeber_count(self):
        return self.memebers.all().count()


class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="group_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Post"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(GroupPost, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))




class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #followers = models.ManyToManyField(User, blank=True, related_name="page_followers")
    followers = models.ManyToManyField(User, blank=True, related_name="page_followers")
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    name = models.CharField(max_length=500, blank=True ,null=True)
    description = models.TextField(blank=True,null=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    category = models.CharField(max_length=30, default="Technology", choices=CATEGORY)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    pid = ShortUUIDField(  max_length=25 )

    def __str__(self):
        if self.name:
            return  self.name
        else:
            return self.user.username


    #def __str__(self):
     #   return self.name

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Page"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(Page, self).save(*args, **kwargs)

    def thumbnail(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />' % self.image.url)
        else:
            return "No Image"

    def followers_count(self):
        return self.followers.all().count()




class PagePost(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="page_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Post"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(PagePost, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))



class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="chat_user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")
    reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
    message = models.CharField(max_length=10000000000)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    mid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        #return self.sender
        return self.user.username

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Chat Message"

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))



class GroupChat(models.Model):
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=10000)
    images = models.FileField(upload_to="group_chat", blank=True, null=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="group_host")
    members = models.ManyToManyField(User, related_name="group_chat_members")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Chat"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(GroupChat, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

    def last_message(self):
        last_message = GroupChatMessage.objects.filter(groupchat=self).order_by("-id").first()
        return last_message

class GroupChatMessage(models.Model):
    groupchat = models.ForeignKey(GroupChat, on_delete=models.SET_NULL, null=True, related_name="group_chat")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="group_chat_message_sender")
    message = models.CharField(max_length=100000)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    mid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")


    def __str__(self):
        return self.groupchat.name

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Chat Messages"







class DevelopersCommunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=10000, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    video = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(  max_length=25 )
    likes = models.ManyToManyField(User, blank=True, related_name="developers_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "DevelopersCommunity"

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(DevelopersCommunity, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

    def gallery_images(self):
        return Gallery.objects.filter(post=self)

    def title_len_count(self):
        return len(self.title)

    def galley_img_count(self):
        return Gallery.objects.filter(post=self).count()

    def post_comments(self):
        comments = Comment.objects.filter(post=self, active=True)
        return comments

    def post_comments_count(self):
        comments_count = Comment.objects.filter(post=self, active=True).count()
        return comments_count






def create_group_profile(sender, instance, created, **kwargs):
    if created :
        Group.objects.create(user=instance)
    pass
def save_group_profile(sender, instance, **kwargs):
    instance.profile.save()

def create_page_profile(sender, instance, created, **kwargs):
    if created:
        Page.objects.create(user=instance)

def save_page_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_page_profile, sender=User)
post_save.connect(save_page_profile, sender=User)
post_save.connect(create_group_profile, sender=User)
post_save.connect(save_group_profile, sender=User)



