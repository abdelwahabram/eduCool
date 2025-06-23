from django.urls import path, include, re_path

from app import views

from rest_framework.routers import DefaultRouter


main_router = DefaultRouter()

main_router.register(r'courses', views.CourseViewSet, basename="course")

main_router.register(r'users', views.UserViewSet, basename="user")

urlpatterns = [
    re_path(r'^courses/(?P<course_pk>\d+)/announcements/?$', views.AnnouncementViewSet.as_view({'get': 'list', 'post': 'create'}), name='announcement-list'),
    
    re_path(r'^announcements/(?P<pk>\d+)/?$', views.AnnouncementViewSet.as_view({'get': 'retrieve'}), name='announcement-detail'),
    
    re_path(r'^courses/(?P<course_pk>\d+)/students/?$', views.StudentViewSet.as_view({'get': 'list'}), name='student-list'),
    
    re_path(r'^announcements/(?P<announcement_pk>\d+)/comments/?$', views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    
    re_path(r'^comments/(?P<pk>\d+)/?$', views.CommentViewSet.as_view({'get': 'retrieve'}), name='comment-detail'),
    
    path('', include(main_router.urls)),

]