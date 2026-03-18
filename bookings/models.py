from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Room(models.Model):
    ROOM_TYPES = [
        ('conference', 'Конференц-зал'),
        ('office', 'Офіс'),
        ('event', 'Зал для заходів'),
        ('coworking', 'Коворкінг'),
    ]

    name = models.CharField(max_length=100, verbose_name='Назва')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name='Тип')
    capacity = models.PositiveIntegerField(verbose_name='Вмістимість (осіб)')
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ціна за день (грн)')
    description = models.TextField(blank=True, verbose_name='Опис')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Кімната'
        verbose_name_plural = 'Кімнати'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def is_available(self, start_date, end_date, exclude_booking_id=None):
        qs = self.bookings.filter(
            status__in=['pending', 'confirmed'],
            start_date__lt=end_date,
            end_date__gt=start_date,
        )
        if exclude_booking_id:
            qs = qs.exclude(pk=exclude_booking_id)
        return not qs.exists()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='Користувач')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name='Кімната')
    start_date = models.DateField(verbose_name='Дата початку')
    end_date = models.DateField(verbose_name='Дата завершення')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примітки')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бронювання'
        verbose_name_plural = 'Бронювання'
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронювання #{self.pk} — {self.room.name} ({self.start_date} – {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('Дата завершення має бути пізніше дати початку.')
            if self.start_date < timezone.now().date():
                raise ValidationError('Дата початку не може бути в минулому.')
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    @property
    def total_price(self):
        return self.duration_days * self.room.price_per_day
