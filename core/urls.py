from django.urls import path

from .views.bible import get_chapter, get_verses


urlpatterns = [
    # path('bible/<str:version>/', views.get_version_info, name='bible-version'),
    # path('bible/<str:version>/<str:book>/', views.get_book_info, name='bible-book'),
    path('bible/<str:version>/<str:book>/<int:chapter>/', get_chapter, name='bible-chapter'),
    path('bible/<str:version>/<str:book>/<int:chapter>/<str:verses>/', get_verses, name='bible-verses'),
]
