from django.urls import path 
from core import views 

app_name = "core"

urlpatterns = [
    # side navigation bars
    path("", views.index, name="feed"),
    path("", views.create_story, name="create_story"),
    path("pages/", views.pages, name="pages"),
    path("pages/mypage", views.mypage, name="mypage"),
    path("pages/newest", views.newest, name="newest"),
    #Creating suggestions forr groups
    #path("groups/suggestion", views.groupssuggestion, name="groupssuggestion"),
    #path("groups/mypage", views.groupsmypage, name="groupsmypage"),
    #path("groups/newest", views.groupsnewest, name="groupsnewest"),

    path("groups/", views.groups, name="groups"),
    path("reels/", views.reels, name="reels"),
    path("blogs/", views.blogs, name="blogs"),
    path("careertutor/", views.careertutor, name="careertutor"),
    path("cbt/", views.cbt, name="cbt"),
    path("events/", views.events, name="events"),
    path("photos/", views.photos, name="photos"),
    path("forum/", views.forum, name="forum"),
    path("birthday/", views.birthday, name="birthday"),
    path("fundraiser/", views.fundraiser, name="fundraiser"),
    path("post/<slug:slug>/", views.post_detail, name="post-detail"),

    path("group_post/", views.group_post, name="group_post"),
    path("my_group_post/", views.my_group_post, name="my_group_post"),
    #creating profile for my group
    path("my_group_profile/", views.my_group_profile, name="my_group_profile"),

    # Chat Feature
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/<username>/", views.inbox_detail, name="inbox_detail"),

    # Group CHat
    path("group-inbox/", views.group_inbox, name="group_inbox"),
    path("group-inbox/<slug:slug>/", views.group_inbox_detail, name="group_inbox_detail"),

    # Join & leave Group
    path("join-group-page/<slug:slug>/", views.join_group_chat_page, name="join_group_chat_page"),
    path("join-group/<slug:slug>/", views.join_group_chat, name="join_group"),
    path("leave-group/<slug:slug>/", views.leave_group_chat, name="leave_group_chat"),

    # Games
    path("all-games/", views.games, name="games"),
    path("stack_brick/", views.stack_brick, name="stack_brick"),

    # Search
    path('search/', views.search_users, name='search_users'),

    # Load more post
    path('load_more_posts/', views.load_more_posts, name='load_more_posts'),

    # creating groups and page
    path("create_group/", views.create_group, name="create_group"),
    path("create_page/", views.create_page, name="create_page"),

    # creating groups and page
    path("about/", views.about, name="about"),






    # Ajax URLs
    path("create-post/", views.create_post, name="create-post"),
    path("like-post/", views.like_post, name="like-post"),
    path("comment-post/", views.comment_on_post, name="comment-post"),
    path("like-comment/", views.like_comment, name="like-comment"),
    path("reply-comment/", views.reply_comment, name="reply-comment"),
    path("delete-comment/", views.delete_comment, name="delete-comment"),
    path("add-friend/", views.add_friend, name="add-friend"),
    path("accept-friend-request/", views.accept_friend_request, name="accept-friend-request"),
    path("reject-friend-request/", views.reject_friend_request, name="reject-friend-request"),
    path("unfriend/", views.unfriend, name="unfriend"),
    path("block-user/", views.block_user, name="block_user"),

]