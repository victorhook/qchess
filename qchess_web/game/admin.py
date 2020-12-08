from django.contrib import admin
from .models import ActiveGame, GameMode, FinishedGame, History


admin.site.register(ActiveGame)
admin.site.register(GameMode)
admin.site.register(FinishedGame)
admin.site.register(History)
