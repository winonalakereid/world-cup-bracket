from django.db import models

#The Team table will store whether or not someone has chosen them to make it into the quarter finals, semi finals, finals or win it all
#The place they can fit in the bracket will be based on their group and rank.
class Team(models.Model):
    country = models.CharField(max_length=50)
    #path to image?
    logo = models.CharField(max_length=400) 
    primary_color = models.CharField(max_length=50)
    secondary_color = models.CharField(max_length=50)
    group = models.CharField(max_length=1)
    group_stage_rank = models.IntegerField(default=0)
    

class TeamRank(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    quarter_finals = models.BooleanField(default=False)
    semi_finals = models.BooleanField(default=False)
    finals = models.BooleanField(default=False)
    winner = models.BooleanField(default=False)
    entry_date = models.DateTimeField('date submitted')