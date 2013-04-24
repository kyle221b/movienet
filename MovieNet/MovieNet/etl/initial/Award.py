import json
import AwardHtmlParser
from bs4 import BeautifulSoup
from movieapp.models import Movie
from movieapp.models import Actor
from movieapp.models import Director
from datetime import datetime

def _getId(name, awardType, idHash, year=None):
	if name in idHash:
		return (idHash[name], idHash)
	
	if awardType == "movie":
		# If it is a movie, then check if the movie is a substring of some query. Then find the shortest result of all matches
		matches = Movie.objects.filter(title__istartswith=name, year__exact=year)
		if not matches:
			match = None
		else:
			bestLength = float("Inf")
			for result in matches:
				result_length = len(result.title)
				if result_length < bestLength:
					match_id = result.id
					match = result.title
					bestLength = result_length
	else:
		if ' ' in name:
			index = name.index(' ')
			name = name[(index + 1):] + ', ' + name[:index]
		if awardType == 'actor':
			match = Actor.objects.filter(name__iexact=name)
		else:
			match = Director.objects.filter(name__iexact=name)
		if match:
			match_id = match[0].id
	
	if not match:
		idHash[name] = None
		return (None, idHash)
	else:
		idHash[name] = match_id
		return (match_id, idHash)

if __name__ == '__main__':
	start = datetime.now()
	actorHeaders = ["ACTOR -- LEADING ROLE", "ACTRESS -- LEADING ROLE", \
					"ACTOR -- SUPPORTING ROLE", "ACTRESS -- SUPPORTING ROLE"]
	directorHeaders = ["DIRECTING", "ASSISTANT DIRECTOR"]
	
	with open("sources/awards.txt") as award_file:
		soup = BeautifulSoup(award_file.read())
	awards = AwardHtmlParser.parseAwards(soup)
	
	AWARD_INDEX = 0
	MOVIE_INDEX = 1
	ACTOR_INDEX = 2
	DIR_INDEX = 3
	
	json_dict = [[], [], [], []]
	count = [1, 1, 1, 1]
	idHash = {}
	for awardHeader, awardNameDict in awards.items():
		for awardName, yearDict in awardNameDict.items():
			years = sorted(list(yearDict.keys()))
			for year in years:
				nominationDict = yearDict[year]
				if '/' in year:
					year = str(int(year[:year.index('/')]) + 1)
				json_dict[AWARD_INDEX].append({'model':'movieapp.award', 'pk':count[AWARD_INDEX], 'fields':{
							'name':awardName, 'year':int(year)}})
				count[AWARD_INDEX] += 1
				for nomination, won in nominationDict.items():
					names = nomination[0]
					movieId, idHash = _getId(nomination[1], "movie", idHash, int(year))
					if not movieId:
						continue
					if not names or (awardHeader not in actorHeaders and awardHeader not in directorHeaders):
						json_dict[MOVIE_INDEX].append({'model':'movieapp.movienomination', 'pk':count[MOVIE_INDEX], 
									'fields':{'movie':movieId, 'award':count[AWARD_INDEX], 'won':won}})
						count[MOVIE_INDEX] += 1
					else:
						for name in names:
							if awardHeader in actorHeaders:
								actorId, idHash = _getId(name, "actor", idHash)
								if actorId:
									json_dict[ACTOR_INDEX].append({'model':'movieapp.actornomination', 
											'pk':count[ACTOR_INDEX], 'fields':{'movie':movieId, 'actor':actorId, 
											'award':count[AWARD_INDEX], 'won':won}})
									count[ACTOR_INDEX] += 1
							elif awardHeader in directorHeaders:
								directorId, idHash = _getId(name, "director", idHash)
								if directorId:
									json_dict[DIR_INDEX].append({'model':'movieapp.directornomination', 
											'pk':count[DIR_INDEX], 'fields':{'movie':movieId, 'director':directorId, 
											'award':count[AWARD_INDEX], 'won':won}})
									count[DIR_INDEX] += 1
	
	with open("../../../movieapp/fixtures/award.json", 'w') as json_file:
		json.dump(json_dict[AWARD_INDEX], json_file, indent=4)
	with open("../../../movieapp/fixtures/movieAward.json", 'w') as json_file:
		json.dump(json_dict[MOVIE_INDEX], json_file, indent=4)
	with open("../../../movieapp/fixtures/actorAward.json", 'w') as json_file:
		json.dump(json_dict[ACTOR_INDEX], json_file, indent=4)
	with open("../../../movieapp/fixtures/directorAward.json", 'w') as json_file:
		json.dump(json_dict[DIR_INDEX], json_file, indent=4)
	
	end = datetime.now()
	print str(start) + '\n' + str(end)
					