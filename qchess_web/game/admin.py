from django.contrib import admin
from .models import ActiveGame, FinishedGame


admin.site.register(ActiveGame)
admin.site.register(FinishedGame)
