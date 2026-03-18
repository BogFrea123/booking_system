from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'capacity', 'price_per_day', 'is_active']
    list_filter = ['room_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'price_per_day']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'room__room_type']
    search_fields = ['user__username', 'user__email', 'room__name']
    list_editable = ['status']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']
