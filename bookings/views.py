from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Room, Booking
from .forms import BookingForm, RoomForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("room_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f"Ласкаво просимо, {user.username}! Реєстрація успішна.")
            return redirect("room_list")
    else:
        form = RegisterForm()
    return render(request, "bookings/register.html", {"form": form})


def room_list(request):
    room_type = request.GET.get('type', '')
    rooms = Room.objects.filter(is_active=True)
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
            available_ids = [r.pk for r in rooms if r.is_available(start_date, end_date)]
            rooms = rooms.filter(pk__in=available_ids)
        except ValueError:
            pass

    return render(request, 'bookings/room_list.html', {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'selected_type': room_type,
    })


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk, is_active=True)
    # Pass busy ranges as JSON for the calendar
    bookings = room.bookings.filter(
        status__in=['pending', 'confirmed'],
        end_date__gte=timezone.now().date(),
    ).values('start_date', 'end_date')
    busy_ranges = [
        {'start': str(b['start_date']), 'end': str(b['end_date'])}
        for b in bookings
    ]
    return render(request, 'bookings/room_detail.html', {
        'room': room,
        'busy_ranges_json': json.dumps(busy_ranges),
    })


@login_required
def booking_create(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk, is_active=True)
    if request.method == 'POST':
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.save()
            messages.success(request, 'Бронювання успішно створено! Очікуйте підтвердження.')
            return redirect('booking_detail', pk=booking.pk)
    else:
        initial = {
            'start_date': request.GET.get('start', ''),
            'end_date': request.GET.get('end', ''),
        }
        form = BookingForm(room=room, initial=initial)
    return render(request, 'bookings/booking_form.html', {'form': form, 'room': room})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST' and booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронювання скасовано.')
    return redirect('my_bookings')


@login_required
def my_bookings(request):
    bookings = request.user.bookings.select_related('room').order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


def availability_api(request, room_pk):
    """JSON endpoint: returns busy date ranges for a room."""
    room = get_object_or_404(Room, pk=room_pk)
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    bookings = room.bookings.filter(
        status__in=['pending', 'confirmed'],
        start_date__year=year,
        start_date__month=month,
    ).values('start_date', 'end_date', 'status')
    data = [{'start': str(b['start_date']), 'end': str(b['end_date']), 'status': b['status']} for b in bookings]
    return JsonResponse({'busy': data})


# --- Admin views ---

def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_bookings(request):
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.select_related('user', 'room').order_by('-created_at')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'bookings/admin_bookings.html', {
        'bookings': bookings,
        'status_choices': Booking.STATUS_CHOICES,
        'selected_status': status_filter,
    })


@user_passes_test(is_admin)
def admin_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Статус бронювання #{pk} оновлено.')
    return redirect('admin_bookings')


@user_passes_test(is_admin)
def admin_room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кімнату додано.')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'bookings/room_form.html', {'form': form, 'action': 'Додати'})


@user_passes_test(is_admin)
def admin_room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кімнату оновлено.')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'bookings/room_form.html', {'form': form, 'action': 'Редагувати', 'room': room})


@user_passes_test(is_admin)
def admin_room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.is_active = False
        room.save()
        messages.success(request, 'Кімнату видалено.')
    return redirect('room_list')
