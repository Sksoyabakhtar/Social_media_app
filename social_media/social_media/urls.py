"""
URL configuration for social_media project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),
    path('admin/deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('admin/activate/<int:user_id>/', views.activate_user, name='activate_user'),
    path('admin/delete/<int:user_id>/', views.delete_user, name='delete_user'),


    path('register/', views.register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('change-password/', login_required(views.change_password), name='change_password'),
    path('logout/',login_required(views.user_logout), name='logout'),
    path('profile/', login_required(views.user_profile), name='user_profile'),

    path('home/', views.home, name='home'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    path('post/', views.post_page, name='post_page'),
    path('remove_profile_pic/', views.remove_profile_pic, name='remove_profile_pic'),

    path('upload-post/', login_required(views.upload_post), name='upload_post'),
    path('edit_post/<int:post_id>/', login_required(views.edit_post), name='edit_post'),
    path('delete_post/<int:post_id>/', login_required(views.delete_post), name='delete_post'),

    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
