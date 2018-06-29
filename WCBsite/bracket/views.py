from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Group, Team, GroupTeam, Match, RoundOf16, Knockout, KnockoutPick, get_group_matches


@login_required
def index(request):
    groups = Group.objects.all()
    group_map = {}
    for group in groups:
        group_map[group.group_name] = []
        group_teams = GroupTeam.objects.filter(group=group).order_by('-team__group_points', '-team__group_goals_scored')

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


@login_required()
def knockout(request):
    r16 = RoundOf16.objects.filter(match__stage=Match.ROUND_OF_16)
    quarters = Knockout.objects.filter(match__stage=Match.QUARTERS)
    picks = KnockoutPick.objects.filter(user__username=request.user)
    quarterPicks = []
    semiPicks = []
    finalPicks = []
    for pick in picks:
        if(pick.knockout.match.stage == "r16"):
            quarterPicks.append(pick)
        elif(pick.knockout.match.stage == "qts"):
            semiPicks.append(pick)
            print(pick.team)
        elif(pick.knockout.match.stage == "sem"):
            finalPicks.append(pick)
        elif(pick.knockout.match.stage == "fin"):
            finalist = pick         
    semis = Knockout.objects.filter(match__stage=Match.SEMIS)
    final = Knockout.objects.filter(match__stage=Match.FINAL)
    context = {
        'round16': r16,
        'quarters': quarters,
        'quarterPicks': quarterPicks,
        'semis': semis,
        'semiPicks': semiPicks,
        'final': final,
        'finalPicks': finalPicks,
        'finalst': finalist
    }
    return render(request, 'knockout.html', context)
