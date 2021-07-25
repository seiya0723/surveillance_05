from django.urls import path
from . import views

app_name    = "surveillance"
urlpatterns = [
    path('', views.index, name="index"),
    path('delete/<int:pk>/', views.delete, name="delete"), #←削除処理の割り当て、<int:pk>は数値であるものをpkという変数に割当て、ビューに渡す。
]
