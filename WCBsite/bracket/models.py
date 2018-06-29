from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

"""
The TeamRank table will store whether a team makes it into the quarter finals, semi finals, finals or win it all
 The place they can fit in the bracket will be based on their group and rank.
"""


def compare_team_ranks(team1, team2):
    if team1.group_points is not team2.group_points:
        return team1.group_points - team2.group_points
    else:
        if team1.group_goal_diff() is not team2.group_goal_diff():
            return team1.group_goal_diff() - team2.group_goal_diff()
        else:
            if team1.group_goals_scored is not team2.group_goals_scored:
                return team1.group_goals_scored - team2.group_goals_scored
            else:
                return team1


class Team(models.Model):
    country = models.CharField(max_length=50)
    fifa_code = models.CharField(max_length=3)
    # path to image
    flag = models.CharField(max_length=400)
    emoji_string = models.CharField(max_length=3)
    group_stage_rank = models.IntegerField(default=0)
    group_points = models.IntegerField(default=0)
    group_goals_allowed = models.IntegerField(default=0)
    group_goals_scored = models.IntegerField(default=0)
    group_wins = models.IntegerField(default=0)
    group_draws = models.IntegerField(default=0)
    group_losses = models.IntegerField(default=0)

    def group_goal_diff(self):
        return self.group_goals_scored - self.group_goals_allowed

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
    ROUND_OF_16 = 'r16'
    QUARTERS = 'qts'
    SEMIS = 'sem'
    FINAL = 'fin'
    ROUNDS = (
        (GROUP_STAGE, "Group Stage"),
        (ROUND_OF_16, "Round of 16"),
        (QUARTERS, "Quarterfinal"),
        (SEMIS, "Semifinal"),
        (FINAL, "Final")
    )

    team1 = models.ForeignKey(Team, related_name='team1', null=True, on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2', null=True, on_delete=models.CASCADE)
    stage = models.CharField(max_length=3, choices=ROUNDS, default=GROUP_STAGE)
    date = models.DateTimeField('kickoff', default=datetime.fromtimestamp(1532044800),
                                help_text='Match kickoff time (UTC)')
    team1_score = models.IntegerField(null=True, default=None, blank=True)
    team2_score = models.IntegerField(null=True, default=None, blank=True)
    team1_penalty = models.IntegerField(null=True, default=None, blank=True)
    team2_penalty = models.IntegerField(null=True, default=None, blank=True)
    winner = models.ForeignKey(Team, related_name='winner', on_delete=models.CASCADE, null=True, blank=True)

    def finished(self):
        try:
            return local_tz(self.date) < local_tz(datetime.now())
        except:
            return False

    def __str__(self):
        if self.finished():
            return f"{self.team1.country} {self.team1.emoji_string} {self.team1_score} - " \
                   f"{self.team2_score} {self.team2.emoji_string} {self.team2.country} {self.date}"
        else:
            return f"{self.team1.country} {self.team1.emoji_string} vs. " \
                   f"{self.team2.emoji_string} {self.team2.country} {self.date}"

    class Meta:
        unique_together = ('team1', 'team2')


class Knockout(models.Model):
    match = models.ForeignKey(Match, related_name='match', on_delete=models.CASCADE, null=True, blank=True)
    prev_match1 = models.ForeignKey('Knockout', related_name='previous_match_1', on_delete=models.CASCADE, null=True, blank=True)
    prev_match2 = models.ForeignKey('Knockout', related_name='previous_match_2', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.match.__str__()


class RoundOf16(Knockout):
    group1 = models.ForeignKey(Group, related_name='team1_group', on_delete=models.CASCADE)
    seed1 = models.IntegerField(choices=((1, "Winner"), (2, "Runner-up")), default=1)
    group2 = models.ForeignKey(Group, related_name='team2_group', on_delete=models.CASCADE)
    seed2 = models.IntegerField(choices=((1, "Winner"), (2, "Runner-up")), default=1)


class GroupPick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} picked {self.team.country}"


class KnockoutPick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    knockout = models.ForeignKey(Knockout, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.__str__()


def get_group_matches():
    groups = Group.objects.all()
    group_matches = {}
    for group in groups:
        # print(f"Querying for group {group}")
        matches = Match.objects.filter(team1__groupteam__group=group, stage=Match.GROUP_STAGE).order_by('date')
        # print(f"Found matches {matches}")
        group_matches[group.group_name] = matches

    # print(group_matches.items())

    return group_matches


def local_tz(date):
    tz = timezone.get_default_timezone()
    return date.astimezone(tz)


def get_group_standings():
    pass
