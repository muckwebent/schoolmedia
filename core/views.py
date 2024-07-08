from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.utils.text import slugify
from django.db.models import OuterRef, Subquery
from django.db.models import Q, Count, Sum, F, FloatField
from django.core.paginator import Paginator

from core.models import Post, Friend, FriendRequest, Notification, Comment, ReplyComment, ChatMessage, GroupChatMessage,GroupPost,GroupChat, Story, DevelopersCommunity, Page, Group
from userauths.models import User, Profile, user_directory_path


import shortuuid

# Notifications Keys
noti_new_like = "New Like"
noti_new_follower = "New Follower"
noti_friend_request = "Friend Request"
noti_new_comment = "New Comment"
noti_comment_liked = "Comment Liked"
noti_comment_replied = "Comment Replied"
noti_friend_request_accepted = "Friend Request Accepted"

@login_required
def index(request):
    story = Story.objects.filter(active=True, visibility="Everyone")
    posts = Post.objects.filter(active=True, visibility="Everyone")



    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    context = {
        "posts":posts,
        "story":story
    }
    return render(request, "core/index.html", context)

@login_required
def post_detail(request, slug):
    post = Post.objects.get(active=True, visibility="Everyone", slug=slug)
    context = {
        "p":post
    }
    return render(request, "core/post-detail.html", context)

def send_notification(user, sender, post, comment, notification_type):
    notification = Notification.objects.create(
        user=user, 
        sender=sender, 
        post=post, 
        comment=comment, 
        notification_type=notification_type
    )
    return notification

@csrf_exempt
def create_post(request):

    if request.method == 'POST':
        title = request.POST.get('post-caption')
        visibility = request.POST.get('visibility')
        image = request.FILES.get('post-thumbnail')

        print("Title ============", title)
        print("thumbnail ============", image)
        print("visibility ============", visibility)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            post = Post(title=title, image=image, visibility=visibility, user=request.user, slug=slugify(title) + "-" + str(uniqueid.lower()))
            post.save()

            
            return JsonResponse({'post': {
                'title': post.title,
                'image_url': post.image.url,
                "full_name":post.user.profile.full_name,
                "profile_image":post.user.profile.image.url,
                "date":timesince(post.date),
                "id":post.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data":"Sent"})


@csrf_exempt
def like_post(request):

    id = request.GET['id']
    post = Post.objects.get(id=id)
    user = request.user
    bool = False 

    if user in post.likes.all():
        post.likes.remove(user)
        bool = False
    else:
        post.likes.add(user)
        bool = True 
        # Do this during noticiation lecture
        if post.user != request.user:
            send_notification(post.user, user, post, None, noti_new_like)

    data = {
        "bool":bool,
        'likes':post.likes.all().count()
    }
    return JsonResponse({"data":data})



@csrf_exempt
def comment_on_post(request):

    id = request.GET['id']
    comment = request.GET['comment']
    post = Post.objects.get(id=id)
    comment_count = Comment.objects.filter(post=post).count()
    user = request.user

    new_comment = Comment.objects.create(
        post=post,
        comment=comment,
        user=user
    )

    # Notifications system
    if new_comment.user != post.user:
        send_notification(post.user, user, post, new_comment, noti_new_comment)


    data = {
        "bool":True,
        'comment':new_comment.comment,
        "profile_image":new_comment.user.profile.image.url,
        "date":timesince(new_comment.date),
        "comment_id":new_comment.id,
        "post_id":new_comment.post.id,
        "comment_count":comment_count + int(1)
    }
    return JsonResponse({"data":data})



@csrf_exempt
def like_comment(request):

    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    user = request.user
    bool = False 

    if user in comment.likes.all():
        comment.likes.remove(user)
        bool = False
    else:
        comment.likes.add(user)
        bool = True 

        # Notifications system
        if comment.user != user:
            send_notification(comment.user, user, comment.post, comment, noti_comment_liked)


    data = {
        "bool":bool,
        'likes':comment.likes.all().count()
    }
    return JsonResponse({"data":data})



@csrf_exempt
def reply_comment(request):

    id = request.GET['id']
    reply = request.GET['reply']

    comment = Comment.objects.get(id=id)
    user = request.user

    new_reply = ReplyComment.objects.create(
        comment=comment,
        reply=reply,
        user=user
    )

    # Notifications system
    if comment.user != user:
        send_notification(comment.user, user, comment.post, comment, noti_comment_replied)

    data = {
        "bool":True,
        'reply':new_reply.reply,
        "profile_image":new_reply.user.profile.image.url,
        "date":timesince(new_reply.date),
        "reply_id":new_reply.id,
        "post_id":new_reply.comment.post.id,
    }
    return JsonResponse({"data":data})


@csrf_exempt
def delete_comment(request):
    id = request.GET['id']
    
    comment = Comment.objects.get(id=id, user=request.user)
    comment.delete()

    data = {
        "bool":True,
    }
    return JsonResponse({"data":data})




@csrf_exempt
def add_friend(request):
    sender = request.user
    receiver_id = request.GET['id'] 
    bool = False

    if sender.id == int(receiver_id):
        return JsonResponse({'error': 'You cannot send a friend request to yourself.'})
    
    receiver = User.objects.get(id=receiver_id)
    
    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            friend_request.delete()
        bool = False
        return JsonResponse({'error': 'Cancelled', 'bool':bool})
    except FriendRequest.DoesNotExist:
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        bool = True
        
        
        send_notification(receiver, sender, None, None, noti_friend_request)

        return JsonResponse({'success': 'Sent',  'bool':bool})


@csrf_exempt
def accept_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()

    receiver.profile.friends.add(sender)
    sender.profile.friends.add(receiver)

    friend_request.delete()

    send_notification(sender, receiver, None, None, noti_friend_request_accepted)

    data = {
        "message":"Accepted",
        "bool":True,
    }
    
    return JsonResponse({'data': data})



@csrf_exempt
def reject_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()
    friend_request.delete()

    data = {
        "message": "Rejected",
        "bool": True,
    }
    return JsonResponse({'data': data})


@csrf_exempt
def unfriend(request):
    sender = request.user
    friend_id = request.GET['id'] 
    bool = False

    if sender.id == int(friend_id):
        return JsonResponse({'error': 'You cannot unfriend yourself, wait a minute how did you even send yourself a friend request?.'})
    
    my_friend = User.objects.get(id=friend_id)
    
    if my_friend in sender.profile.friends.all():
        sender.profile.friends.remove(my_friend)
        my_friend.profile.friends.remove(sender)
        bool = True
        return JsonResponse({'success': 'Unfriend Successfull',  'bool':bool})
    
    


@login_required
def inbox(request):
    user_id = request.user

    chat_message = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")
    
    context = {
        'chat_message': chat_message,
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def inbox_detail(request, username):
    user_id = request.user
    message_list = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")


    
    sender = request.user
    receiver = User.objects.get(username=username)
    receiver_details = User.objects.get(username=username)
    
    messages_detail = ChatMessage.objects.filter(
        Q(sender=sender, reciever=receiver) | Q(sender=receiver, reciever=sender)
    ).order_by("date")

    messages_detail.update(is_read=True)
    
    if messages_detail:
        r = messages_detail.first()
        reciever = User.objects.get(username=r.reciever)
    else:
        reciever = User.objects.get(username=username)

    context = {
        'message_detail': messages_detail,
        "reciever":reciever,
        "sender":sender,
        "receiver_details":receiver_details,
        "message_list":message_list,
    }
    return render(request, 'chat/inbox_detail.html', context)


def block_user(request):
    id = request.GET['id']
    user = request.user
    friend = User.objects.get(id=id)

    if user.id == friend.id:
        return JsonResponse({'error': 'You cannot block yourself'})


    if friend in user.profile.friends.all():
        user.profile.blocked.add(friend)
        user.profile.friends.remove(friend)
        friend.profile.friends.remove(user)
    else:
        return JsonResponse({'error': 'You cannot block someone that is not your friend'})

    return JsonResponse({'success': 'User Blocked'})


@login_required
def group_inbox(request):
    groupchat = GroupChat.objects.filter(members__in=User.objects.filter(pk=request.user.pk), active=True)
    print("groupchat =============", groupchat)
    context = {
        'groupchat': groupchat,
    }
    return render(request, 'chat/group_inbox.html', context)


@login_required
def group_inbox_detail(request, slug):
    groupchat_list = GroupChat.objects.filter(members__in=User.objects.filter(pk=request.user.pk), active=True)
    groupchat = GroupChat.objects.get(slug=slug, active=True)
    group_messages = GroupChatMessage.objects.filter(groupchat=groupchat).order_by("id")

    if request.user not in groupchat.members.all():
        return redirect("core:join_group_chat_page", groupchat.slug)


    context = {
        'groupchat': groupchat,
        'group_name': groupchat.slug,
        'group_messages': group_messages,
        'groupchat_list': groupchat_list,
    }
    return render(request, 'chat/group_inbox_detail.html', context)

def join_group_chat_page(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    context = {
        'groupchat': groupchat,
    }
    return render(request, 'chat/join_group_chat_page.html', context)


def join_group_chat(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    if request.user in groupchat.members.all():
        return redirect("core:group_inbox_detail", groupchat.slug)
    
    groupchat.members.add(request.user)
    return redirect("core:group_inbox_detail", groupchat.slug)


def leave_group_chat(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    if request.user in groupchat.members.all():
        groupchat.members.remove(request.user)
        return redirect("core:join_group_chat_page", groupchat.slug)

    return redirect("core:join_group_chat_page", groupchat.slug)


def games(request):
    return render(request, 'games/all_games.html')

def stack_brick(request):
    return render(request, 'games/stack_brick.html')


def search_users(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(username__icontains=query) | User.objects.filter(email__icontains=query) | User.objects.filter(full_name__icontains=query)

        users_data = []
        for user in users:
            try:
                profile = Profile.objects.get(user=user)
                profile_image = profile.image.url
                full_name = profile.full_name
            except Profile.DoesNotExist:
                profile_image = None
                full_name = None

            user_data = {
                'username': user.username,
                'full_name': full_name,
                'email': user.email,
                'profile_image': profile_image,
            }
            users_data.append(user_data)
    else:
        users_data = []
    return JsonResponse({'users': users_data})




def load_more_posts(request):
    all_posts = Post.objects.filter(active=True, visibility="Everyone").order_by('-date')

    # Paginate the posts
    paginator = Paginator(all_posts, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    posts_data = []
    for post in page_obj:
        post_data = {
            'title': post.title,
            'profile_image': post.user.profile.image.url,
            'full_name': post.user.profile.full_name,
            'image_url': post.image.url if post.image else None,
            'video': post.video.url if post.video else None,
            'id': post.id,
            'id': post.id,
            'likes': post.likes.count(),
            'slug': post.slug,
            'views': post.views,
            'date': timesince(post.date),
        }
        posts_data.append(post_data)

    return JsonResponse({'posts': posts_data})


@login_required
def story(request):
    stories = Story.objects.all()
    context = {
        "story": stories
    }
    return render(request, "core/index.html", context)

# View for creating a new story
def create_story(res):
    if request.method == "POST":
        title = res.POST.get("story-caption")
        visibility = res.POST.get("visibility")
        image = res.FILES.get("story-thumbnail")

        print("Title ============", title)
        print("thumbnail ============", image)
        print("visibility ============", visibility)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            story = Story(title=title, image=image, visibility=visibility, user=request.user,
                        slug=slugify(title) + "-" + str(uniqueid.lower()))
            story.save()

            return JsonResponse({'story': {
                'title': story.title,
                'image_url': story.image.url,
                "full_name": story.user.profile.full_name,
                "profile_image": story.user.profile.image.url,
                "date": timesince(story.date),
                "id": story.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data": "Sent"})


def pages(res):
    page = Page.objects.all()
    context = {
        "page":page
    }
    return render(res, 'core/pages.html', context)

def mypage(res):
    page = Page.objects.all()
    context = {
        "page":page
    }
    return render(res, 'core/mypage.html', context)

def newest(res):
    page = Page.objects.all()
    context = {
        "page":page
    }
    return render(res, 'core/newest.html', context)



def groups(res):
    return render(res, 'core/groups.html')

def careertutor(res):
    return render(res, 'core/careertutor.html')

def cbt(res):
    return render(res, 'core/cbt.html')
def reels(res):
    return render(res, 'core/reels.html')
def events(res):
    return render(res, 'core/event.html')
def photos(res):
    return render(res, 'core/albums.html')
def forum(res):
    return render(res, 'core/forum.html')
def birthday(res):
    return render(res, 'core/birthday.html')
def fundraiser(res):
    return render(res, 'core/fundraiser.html')
def blogs(res):
    return render(res, 'core/blogs.html')



@login_required
def about(request):
    about = DevelopersCommunity.objects.filter(active=True, visibility="Everyone")




    paginator = Paginator(about, 1)
    page_number = request.GET.get('page')
    about = paginator.get_page(page_number)
    context = {
        "about":about

    }
    return render(request, "core/about.html", context)

@login_required
def group_post(res):
    posts = GroupPost.objects.filter(active=True,visibility="Everyone")
    context = {
        "posts":posts
    }
    return render(res,'core/newestgroup.html', context)


@login_required
def my_group_profile(request):
    profile = request.user.profile
    posts = GroupPost.objects.filter(active=True, user=request.user)

    context = {
        "posts":posts,
        "profile":profile,
    }
    return render(request, "core/my-group-profile.html", context)


@login_required
def my_group_post(request):
    user_profile = Profile.objects.get(user=request.user)
    following_users = user_profile.followings.all()
    posts = GroupPost.objects.filter(user__in=following_users, active=True).order_by('-date')
    context = {
        'posts': posts
    }
    return render(request, 'core/my_group_post.html', context)

@csrf_exempt
def create_page(res):
    if res.method == "POST":
        name = res.POST.get("page_name")
        category = res.FILES.get("page_category")
        description = res.FILES.get("page_description")

        print("Page_name ============", name)
        print("Page_category ============", category)
        print("Page_description ============", description)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if name and category:
            page = Page(name=name, category=category, visibility=visibility, user=res.user,
                        slug=slugify(name) + "-" + str(uniqueid.lower()))
            story.save()

            return JsonResponse({'page': {
                'name': page.name,
                'image_url': page.image.url,
                "date": timesince(story.date),
                "id": page.pid,
            }})
        else:
            return render(res,'core/create-page.html')
    return render(res,'core/create-page.html')

@csrf_exempt
def create_group(request):
    if request.method == "POST":
        name = res.POST.get("page_name")
        category = res.FILES.get("page_category")
        description = res.FILES.get("page_description")

        print("Page_name ============", name)
        print("Page_category ============", category)
        print("Page_description ============", description)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if name and category:
            page = Page(name=name, category=category, visibility=visibility, user=request.user,
                        slug=slugify(name) + "-" + str(uniqueid.lower()))
            story.save()

            return JsonResponse({'story': {
                'name': page.name,
                'image_url': page.image.url,
                "date": timesince(story.date),
                "id": page.pid,
            }})
        else:
            return JsonResponse({'error': 'Invalid Page data'})

    else:
        return render(request,'core/create-group.html')
