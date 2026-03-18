from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Rooms
    path('', views.room_list, name='room_list'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_pk>/book/', views.booking_create, name='booking_create'),

    # User bookings
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    # API
    path('api/rooms/<int:room_pk>/availability/', views.availability_api, name='availability_api'),

    # Admin
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/bookings/<int:pk>/update/', views.admin_booking_update, name='admin_booking_update'),
    path('admin-panel/rooms/add/', views.admin_room_create, name='admin_room_create'),
    path('admin-panel/rooms/<int:pk>/edit/', views.admin_room_edit, name='admin_room_edit'),
    path('admin-panel/rooms/<int:pk>/delete/', views.admin_room_delete, name='admin_room_delete'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='bookings/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
]
