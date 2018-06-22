from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

"""
The TeamRank table will store whether a team makes it into the quarter finals, semi finals, finals or win it all
 The place they can fit in the bracket will be based on their group and rank.
"""


class Team(models.Model):
    country = models.CharField(max_length=50)
    fifa_code = models.CharField(max_length=3)
    # path to image
    flag = models.CharField(max_length=400)
    emoji_string = models.CharField(max_length=3)
    group_stage_rank = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.country} {self.emoji_string}"


class Group(models.Model):
    group_name = models.CharField(max_length=15)

    def __str__(self):
        return self.group_name


class GroupTeam(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.group}: {self.team}"


class TeamRank(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    quarter_finals = models.BooleanField(default=False)
    semi_finals = models.BooleanField(default=False)
    finals = models.BooleanField(default=False)
    winner = models.BooleanField(default=False)
    entry_date = models.DateTimeField('date submitted')


class Match(models.Model):
    GROUP_STAGE = 'grp'
    QUARTERS = 'qts'
    SEMIS = 'sem'
    FINAL = 'fin'
    ROUNDS = (
        (GROUP_STAGE, "Group Stage"),
        (QUARTERS, "Quarterfinal"),
        (SEMIS, "Semifinal"),
        (FINAL, "Final")
    )

    team1 = models.ForeignKey(Team, related_name='team1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2', on_delete=models.CASCADE)
    stage = models.CharField(max_length=3, choices=ROUNDS, default=GROUP_STAGE)
    date = models.DateTimeField('kickoff', default='2018-06-22 00:00:00', help_text='Match kickoff time (UTC)')
    team1_score = models.IntegerField(null=True, default=None, blank=True)
    team2_score = models.IntegerField(null=True, default=None, blank=True)
    team1_penalty = models.IntegerField(null=True, default=None, blank=True)
    team2_penalty = models.IntegerField(null=True, default=None, blank=True)
    winner = models.ForeignKey(Team, related_name='winner', on_delete=models.CASCADE, null=True, blank=True)
    # finished = models.BooleanField(default=False)

    def __str__(self):
        if self.winner is not None:
            return f"{self.team1.country} {self.team1.emoji_string} {self.team1_score} - " \
                   f"{self.team2_score} {self.team2.emoji_string} {self.team2.country} {self.date}"
        else:
            return f"{self.team1.country} {self.team1.emoji_string} vs. " \
                   f"{self.team2.emoji_string} {self.team2.country} {self.date}"

    class Meta:
        unique_together = ('team1', 'team2')


class Pick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} picked {self.team.country}"


def get_group_matches():
    groups = Group.objects.all()
    group_matches = {}
    for group in groups:
        print(f"Querying for group {group}")
        matches = Match.objects.filter(team1__groupteam__group=group, stage=Match.GROUP_STAGE).order_by('date')
        print(f"Found matches {matches}")
        group_matches[group.group_name] = matches

    print(group_matches.items())

    return group_matches

def to_tz(date):
    local_tz = timezone.get_default_timezone()
    return date.astimezone(local_tz)


def get_group_standings():
    teams = Team.objects.all()
    points = {}
    for team in teams:
        points[team.country] = 0
    # for team in teams:
    #     matches = Match.objects.filter(Q(team1__country=team) | Q(team2__country=team))
    matches = Match.objects.all()
    for match in matches:
        print(match)
        print(to_tz(match.date))
        print(to_tz(datetime.now()))
        print(f"In the past? {to_tz(match.date) < to_tz(datetime.now())}")
        if match.winner is not None:
            points[match.winner.country] += 3
        elif to_tz(match.date) < to_tz(datetime.now()):
            points[match.team1.country] += 1
            points[match.team2.country] += 1
    print(f"Points: {points}")
