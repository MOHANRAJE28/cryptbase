
from django.contrib import admin
from django.urls import path
from UploadFiles    import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('uploadfile/',views.uploadfile,name="uploadfile"),
    path('deleteFile/<int:id>/',views.deleteFile),
    path('download/<int:id>/', views.download_file, name='download_file'),
    path('Login/', views.login_view, name='login'),
    path('Signup/', views.signup_view, name='signup'),
    path('DecryptFiles/', views.decrypt, name='DecryptFile'),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 