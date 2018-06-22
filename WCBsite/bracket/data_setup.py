from .models import Team, Group, GroupTeam, Match
import json, os


def create_teams():
    pwd = os.path.dirname(__file__)
    print(f"Current directory {pwd}")
    file_path = os.path.join(pwd, 'source-data.json')
    with open(file_path) as f:
        data = json.load(f)

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
            home = match['home_result']
            away = match['away_result']
            winner = None
            if match['finished']:
                if home > away:
                    winner = team1
                elif away > home:
                    winner = team2
            m = Match(team1=team1, team2=team2, team1_score=home, team2_score=away, winner=winner, date=match['date'])
            m.save()
            print(f"Created match {m}")


def create(apps, schema_editor):
    create_teams()


def revert(apps, schema_editor):
    print("Wipe data clean")
    Team.objects.all().delete()
    Group.objects.all().delete()
    GroupTeam.objects.all().delete()
    Match.objects.all().delete()
