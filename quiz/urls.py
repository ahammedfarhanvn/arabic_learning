from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'quiz'

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("quiz/<str:category>/<int:level>/", views.quiz_view, name="quiz_view"),
    path("category/<str:category>/", views.category_detail, name="category_detail"),
    path('import-questions/', views.import_questions, name='import_questions'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


