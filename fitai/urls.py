from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Імпортуй views з fitness (тут ти додаєш шлях до metrics)
from fitness.views import metrics  # ← це важливо! без цього path('metrics/') не знайде функцію

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fitness.urls')),  # підключення твого app (onboarding, history тощо)
    path('metrics/', metrics, name='metrics'),  # окремий шлях до метрик
]

# Роздача медіа-файлів у розробці (фото з /media/)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
