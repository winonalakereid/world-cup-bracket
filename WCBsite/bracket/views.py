from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Group, Team, GroupTeam, Match, get_group_matches, get_group_standings


@login_required
def index(request):
    groups = Group.objects.all()
    group_map = {}
    for group in groups:
        group_map[group.group_name] = []
        group_teams = GroupTeam.objects.filter(group=group)
        for ref in group_teams:
            group_map[group.group_name].append(ref.team)
    context = {
        'group_map': group_map
    }
    return render(request, 'groups.html', context)


@login_required()
def matches(request):
    group_matches = get_group_matches()
    context = {
        'group_matches': group_matches
    }
    return render(request, 'matches.html', context)
