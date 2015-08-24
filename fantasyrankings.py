import csv 

# Reference for stats:
# 0 : g
# 1 : a
# 2 : pts
# 3 : diff
# 4 : pim
# 5 : hits
# 6 : blocks
# 7 : ppg
# 8 : ppa
# 9 : shg
# 10 : sha
# 11 : gw
# 12 : sog

class PlayerInfo:
    def __init__(self, playerstats):
        self.name = playerstats[0]
        self.team = playerstats[1]
        self.gp = int(float(playerstats[2]))
        self.stats = [0]*13
        for i in range(0,13):
            self.stats[i] = int(float(playerstats[i+3]))
        self.totalrawscore = 0
    
    #def __str__(self):
    #    return "{!s}: {:d} {:d} {:d} {:d} {:d} {:d} {:d} {:d} {:d}".format(self.name, self.gp, self.stats, self.a, self.pts, self.diff, self.pim, self.hits, self.blocks, self.sog)
        
    def addRawScores(self, pergame_league_avgs):
        self.rawscores = []
        for i in range(0,len(pergame_league_avgs)):
            statpergame = float(self.stats[i])/float(self.gp)
            self.rawscores.append(float(statpergame)/float(pergame_league_avgs[i]))
    
    def computeTotalScore(self,categories_counted):
        for i in range(0,len(categories_counted)):
            if categories_counted[i] == 1:
                self.totalrawscore += self.rawscores[i]

def parseStats():

    # Create new array to put players into
    playerInfoArray = []
    
    statfile = open('nhl-yahoo.csv',"rb")
    reader = csv.reader(statfile)
    
    rownum = 0
    for row in reader:
        # Save header
        if rownum == 0:
            header = row
        else:
            # create new player entry
            playerStats = []
            for col in row: 
                if col == 'N/A':
                    col = 0
                playerStats.append(col)   
            # Create new player instance
            playerEntry = PlayerInfo(playerStats)
            playerInfoArray.append(playerEntry)            
        rownum += 1
    statfile.close()
    
    return playerInfoArray
    
def calculateLeagueTotals(arr):
    stats_sum = [0]*13
    games_played_sum = 0
    players_significant_num = 0
    
    normalized_league_avgs = []
    unnormalized_league_avgs = []
    # loop through all players
    for player in arr:
        if player.gp >= 20:
            players_significant_num += 1
            games_played_sum += player.gp
            for i in range(0,13):
                stats_sum[i] += player.stats[i]
  
    # Calculate averages and return
    for i in range (0,13):
        normalized_league_avgs.append(float(stats_sum[i])/float(games_played_sum))
        unnormalized_league_avgs.append(float(stats_sum[i])/float(players_significant_num))  
        
    return normalized_league_avgs        

    
def main():

    # Set up player list and assign by parsing csv file
    playerInfoArray = parseStats()
    
    # assume all goals, assists, points, blocks, hits, pim counts
    cats_counted = [1,1,1,0,1,1,1,0,0,0,0,0,1]
    
    # Experiment (sort players by hits)
    #playerInfoArray.sort(key=lambda x: x.hits, reverse=True)
    
    # compute league averages for players with more than 20 games played
    pergame_league_avgs = calculateLeagueTotals(playerInfoArray)
    print  [elem*82 for elem in pergame_league_avgs] 
    
    # loop through and compute/add raw scores to playerinfo
    for player in playerInfoArray:
        player.addRawScores(pergame_league_avgs)
        player.computeTotalScore(cats_counted)
        
    # sort by total scores
    playerInfoArray.sort(key=lambda x : x.totalrawscore,reverse=True)
        
    # Test (print out top 20)
    for i in range(0, 50):
        if playerInfoArray[i].gp >= 20:
            playerString = playerInfoArray[i].name + ' ' + str(playerInfoArray[i].gp) + ' ' +str(playerInfoArray[i].totalrawscore) 
            #print playerString
            #for j in range(0,len(cats_counted)):
            #    if cats_counted[j] == 1:
            #       playerString += str(playerInfoArray[i].stats
               
if __name__ == "__main__":
    main()