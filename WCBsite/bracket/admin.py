from django.contrib import admin
from .models import Team, Group, GroupTeam, Match, GroupPick, Knockout, KnockoutPick

# Register your models here.

admin.site.register(Team)
admin.site.register(Group)
admin.site.register(GroupTeam)
admin.site.register(Match)
admin.site.register(GroupPick)
admin.site.register(Knockout)
admin.site.register(KnockoutPick)