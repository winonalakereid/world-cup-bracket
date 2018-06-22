from django.contrib import admin
from .models import Team, Group, GroupTeam, Match, Pick

# Register your models here.

admin.site.register(Team)
admin.site.register(Group)
admin.site.register(GroupTeam)
admin.site.register(Match)
admin.site.register(Pick)