from .models import Team, Group, GroupTeam, Match, RoundOf16
import json
import os
import re

def load_json():
    pwd = os.path.dirname(__file__)
    print(f"Current directory {pwd}")
    file_path = os.path.join(pwd, 'source-data.json')
    with open(file_path) as f:
        data = json.load(f)
        return data

def create_teams(data):
    # print(data['groups'])
    # Create teams
    for team in data['teams']:
        t = Team(pk=team['id'], country=team['name'], fifa_code=team['fifaCode'], flag=team['flag'], emoji_string=team['emojiString'])
        t.save()

    team_map = {
        'A': ['Russia', 'Uruguay', 'Egypt', 'Saudi Arabia'],
        'B': ['Spain', 'Portugal', 'Iran', 'Morocco'],
        'C': ['France', 'Denmark', 'Australia', 'Peru'],
        'D': ['Croatia', 'Iceland', 'Argentina', 'Nigeria'],
        'E': ['Serbia', 'Brazil', 'Switzerland', 'Costa Rica'],
        'F': ['Sweden', 'Mexico', 'Germany', 'South Korea'],
        'G': ['Belgium', 'England', 'Tunisia', 'Panama'],
        'H': ['Japan', 'Senegal', 'Poland', 'Colombia']
    }
    # Create Groups and Group/Team Membership
    for group, teams in team_map.items():
        g = Group(group_name=f"Group {group}")
        g.save()
        print(f"Created group {g}")

        for team in teams:
            t = Team.objects.get(country=team)

            gt = GroupTeam(group=g, team=t)
            gt.save()
            print(f"Connected team to group {g}, {t}")

    # Create matches
    for key, group in data['groups'].items():
        for match in group['matches']:
            team1 = Team.objects.get(pk=match['home_team'])
            team2 = Team.objects.get(pk=match['away_team'])
            team1_score = match['home_result']
            team2_score = match['away_result']
            winner = None
            if match['finished']:
                if team1_score > team2_score:
                    winner = team1
                elif team2_score > team1_score:
                    winner = team2
            m = Match(team1=team1, team2=team2, team1_score=team1_score, team2_score=team2_score, winner=winner,
                      date=match['date'])
            m.save()
            print(f"Created match {m}")


def calculate_points():
    matches = Match.objects.filter(stage=Match.GROUP_STAGE)
    for match in matches:
        print(f"Calculating points for {match}")

        # update points, w/l/d
        if match.winner is not None:
            if match.winner.pk is match.team1.pk:
                print(f"Winner: {match.team1}, {match.team1.group_points}")
                match.team2.group_losses += 1
                match.team1.group_points += 3
                match.team1.group_wins += 1
            else:
                print(f"Winner: {match.team2}, {match.team2.group_points}")
                match.team1.group_losses += 1
                match.team2.group_points += 3
                match.team2.group_wins += 1
        elif match.finished():
            print(f"Draw")
            # draw
            match.team1.group_draws += 1
            match.team2.group_draws += 1

            match.team1.group_points += 1
            match.team2.group_points += 1
        print(f"Wins: {match.team1}:{match.team1.group_wins}, {match.team2}:{match.team2.group_wins}")
        print(f"Draws: {match.team1}:{match.team1.group_draws}, {match.team2}:{match.team2.group_draws}")
        print(f"Losses: {match.team1}:{match.team1.group_losses}, {match.team2}:{match.team2.group_losses}")

        print(f"Points: {match.team1}:{match.team1.group_points}, {match.team2}:{match.team2.group_points}")

        # update scores
        if match.finished():
            match.team1.group_goals_scored += match.team1_score
            match.team2.group_goals_allowed += match.team1_score
            match.team2.group_goals_scored += match.team2_score
            match.team1.group_goals_allowed += match.team2_score
        match.team1.save()
        match.team2.save()
        print(f"Match: {match.team1} {match.team1.group_points}, {match.team2} {match.team2.group_points} ")


def calculate_ranks():
    groups = Group.objects.all()
    for group in groups:
        teams = GroupTeam.objects.filter(group=group).order_by('-team__group_points')
        print(teams)
        i = 1
        for gt in teams:
            gt.team.group_stage_rank = i
            gt.team.save()
            i += 1
            print(f"{gt.group}: {gt.team} points: {gt.team.group_points} rank: {gt.team.group_stage_rank}")


def get_group_seed(match):
    seed = None
    print(f"Matches: {match.group(1)}, {match.group(2)}")
    if match.group(1) == 'winner':
        seed = 1
    elif match.group(1) == 'runner':
        seed = 2
    group_name = f"Group {match.group(2).upper()}"
    return group_name, seed


def create_knockouts(knockout):
    round16 = knockout['round_16']
    matches = round16['matches']
    for match in matches:
        print(f"Home {match['home_team']}, Away {match['away_team']}")
        m = re.search('(winner|runner)_([a-h])', match['home_team'])
        (g1_name, g1_seed) = get_group_seed(m)
        group1 = Group.objects.get(group_name=g1_name)
        m = re.search('(winner|runner)_([a-h])', match['away_team'])
        (g2_name, g2_seed) = get_group_seed(m)
        group2 = Group.objects.get(group_name=g2_name)

        print(f"Searching for group team: {g1_name}, {g1_seed}")
        group = GroupTeam.objects.filter(group__group_name=g1_name).order_by('team__group_stage_rank')
        for gt in group:
            print(f"{gt.group}: {gt.team}, {gt.team.group_stage_rank}")
        gteam1 = GroupTeam.objects.get(group__group_name=g1_name, team__group_stage_rank=g1_seed)
        gteam2 = GroupTeam.objects.get(group__group_name=g2_name, team__group_stage_rank=g2_seed)

        match = Match(team1=gteam1.team, team2=gteam2.team, team1_score=match['home_result'], team1_penalty=match['home_penalty'],
                      team2_score=match['away_result'], team2_penalty=match['away_penalty'], stage=Match.ROUND_OF_16)
        match.save()

        r = RoundOf16(match=match, group1=group1, seed1=g1_seed, group2=group2, seed2=g2_seed)
        r.save()

def create(apps, schema_editor):
    data = load_json()
    create_teams(data)
    calculate_points()
    calculate_ranks()
    create_knockouts(data['knockout'])


def revert(apps, schema_editor):
    print("Wipe data clean")
    Team.objects.all().delete()
    Group.objects.all().delete()
    GroupTeam.objects.all().delete()
    Match.objects.all().delete()
