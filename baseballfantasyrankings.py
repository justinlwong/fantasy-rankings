import MySQLdb
import sys
import math

# Reference for stats:

# 0 : r
# 1 : hr
# 2 : rbi
# 3 : sb 
# 4 : avg (h/ab)
# 5 : obp (h + bb + hbp)/ (ab + bb + hbp + sf)

# Source file columns 

# 0 : g
# 1 : ab
# 2 : r
# 3 : h
# 4 : hr
# 5 : rbi
# 6 : sb
# 7 : bb
# 8 : hbp
# 9 : sf


class PlayerInfo:
    def __init__(self, id, first, last, year, stint, firstyearstats):
        self.id = id
        self.first = first
        self.last = last
        self.stats = {}
        self.addYearStats(year, stint, firstyearstats)
        self.totalrawscore = 0
        self.sums = [0]*10
        self.total_avgs = [0]*8 
        self.yavgs = {}       
        self.yearlyRawScores = {}
        self.yearlyTotalRawScore = {}   
        self.trendScores = [0]*6
        self.totalTrendScore = 0        
        self.yearsSignificant = []
        self.positionsEligible = {}
        
    def addYearStats(self, year, stint, stats):
        year = int(year)
        yearstats = [0]*10
        for i in range(0,10):           
            yearstats[i] = int(float(str(stats[i])))
        if stint == 1:
            self.stats[year] = yearstats
        else:                 
            # add to existing one
            if year in [k for k,v in self.stats.items()]:
                temp = self.stats[year]
                for i in range(0,10):
                    temp[i] += yearstats[i]
                self.stats[year] = temp
                
    def addStintPositionStats(self,year, stint, pos, g, gs):
        year = int(year)
        if year not in [k for k,v in self.positionsEligible.items()]:
            # create new entry
            self.positionsEligible[year] = []
        
        # check if 5 gs or 10 g
        if g >= 10 or gs >= 5 and (pos not in self.positionsEligible[year]):
            self.positionsEligible[year].append(pos)
                
                
    def calculateYearlyAverageStats(self, year):
        if year in [k for k,v in self.stats.items()]:
            self.yavgs[year] = [0]*8

            yearStats = self.stats[year]
            
            self.yavgs[year][0] = yearStats[0]           
            self.yavgs[year][1] = yearStats[1]
            
            if self.yavgs[year][1] >= 250:
                self.yearsSignificant.append(year)
            
            if yearStats[0] != 0 and yearStats[1] != 0:
                self.yavgs[year][2] = float(yearStats[2])/float(yearStats[0])        
                self.yavgs[year][3]  = float(yearStats[4])/float(yearStats[0]) 
                self.yavgs[year][4]  = float(yearStats[5])/float(yearStats[0]) 
                self.yavgs[year][5]  = float(yearStats[6])/float(yearStats[0]) 
                self.yavgs[year][6]  = float(yearStats[3])/float(yearStats[1])
                self.yavgs[year][7]  = float(yearStats[3] + yearStats[7] + yearStats[8])/float(yearStats[1] + yearStats[7] + yearStats[8] + yearStats[9])        
                
    def calculateAverageFantasyStats(self):
        arrayFromDict = [v for k,v in self.stats.items()]
        
        stat_sum = [0]*10
        
        for yearStats in arrayFromDict:
            for i in range(0,10):
                stat_sum[i] += yearStats[i]
                
        self.sums = stat_sum        

        self.total_avgs[0] = stat_sum[0]  
        self.total_avgs[1] = stat_sum[1]        
        
        if stat_sum[0] != 0 and stat_sum[1] != 0:
            self.total_avgs[2] = float(stat_sum[2])/float(stat_sum[0])        
            self.total_avgs[3]  = float(stat_sum[4])/float(stat_sum[0]) 
            self.total_avgs[4]  = float(stat_sum[5])/float(stat_sum[0]) 
            self.total_avgs[5]  = float(stat_sum[6])/float(stat_sum[0]) 
            self.total_avgs[6]  = float(stat_sum[3])/float(stat_sum[1])
            self.total_avgs[7]  = float(stat_sum[3] + stat_sum[7] + stat_sum[8])/float(stat_sum[1] + stat_sum[7] + stat_sum[8] + stat_sum[9])
            
    def addYearlyRawScores(self, year, yearLeagueAvgs, yearLeagueStdDevs):
        if year in [k for k,v in self.stats.items()]: 
            self.yearlyRawScores[year] = []  
            for i in range(0,len(yearLeagueAvgs)-2):
                self.yearlyRawScores[year].append((float(self.yavgs[year][i+2] - yearLeagueAvgs[i+2])/float(yearLeagueStdDevs[i])))   
                            
    def addTotalRawScores(self, pergame_league_avgs, std_devs):
        self.rawscores = []
        for i in range(0,len(pergame_league_avgs)-2):
            self.rawscores.append((float(self.total_avgs[i+2] - pergame_league_avgs[i+2])/float(std_devs[i])))

    def computeYearlyTotalScore(self,year,categories_counted):
        if year in [k for k,v in self.stats.items()]: 
            self.yearlyTotalRawScore[year] = 0
            for i in range(0,len(categories_counted)):
                if categories_counted[i] == 1:
                    self.yearlyTotalRawScore[year] += self.yearlyRawScores[year][i]
                
    def computeTotalScore(self,categories_counted):
        for i in range(0,len(categories_counted)):
            if categories_counted[i] == 1:
                self.totalrawscore += self.rawscores[i]
                
    def calculateTrendScores(self):
        yearsSignificantList = self.yearsSignificant
        trends = [0]*6
        total_trend = 0
        for year in yearsSignificantList:
            if (year +1) in yearsSignificantList:
                for i in range(0,len(self.yearlyRawScores[year])):
                    trends[i] += (self.yearlyRawScores[year+1][i] - self.yearlyRawScores[year][i])
                total_trend += (self.yearlyTotalRawScore[year+1] - self.yearlyTotalRawScore[year])
        if len(yearsSignificantList) > 1:
            self.trendScores = [float(elem)/float(len(yearsSignificantList)-1) for elem in trends]
            self.totalTrendScore = float(total_trend)/float(len(yearsSignificantList)-1)       
        
def getStats():
   
    db = None
    playerInfoArray = []
    
    try:
        # Connect to DB
        db = MySQLdb.connect(host="localhost",user="root",passwd="jays1234",db="lahman")
        cursor = db.cursor()        
                            
        # Query for 2012, 2011, 2010 
        cursor.execute("SELECT master.playerID, master.nameFirst, master.nameLast, batting.yearID, batting.stint, batting.G," +  
                   "batting.AB, batting.R, batting.H, batting.HR, batting.RBI, batting.SB, batting.BB," + 
                    "batting.HBP, batting.SF FROM batting,master WHERE batting.playerID = master.playerID " + 
                    "AND batting.yearID > 2009;" )
        
        rows = cursor.fetchall()   

        cursor = db.cursor()  
        cursor.execute("SELECT playerID,yearID,stint,POS,G,GS "+
                       "FROM fielding") 
        positionRows = cursor.fetchall()                       
        
    except MySQLdb.Error,e:
        print "Error with database connection"
        sys.exit(1)
    finally:
        # use data
        
        currentID = None
        curPlayerEntry = None
        
        for row in rows:
            if row[6] != None:
                stint = row[4]
                stats = row[5:15]
                year = str(row[3])
                if row[0] != currentID:
                    # add previous player entry to array
                    if curPlayerEntry != None:
                         playerInfoArray.append(curPlayerEntry)

                    # set up new player entry
                    currentID = row[0]
                    firstname = row[1]
                    lastname = row[2]

                    # create new playerInfo object
                    curPlayerEntry = PlayerInfo(currentID, firstname, lastname, year, stint, stats)
                else: 
                    curPlayerEntry.addYearStats(year, stint, stats)            
        
        for row in positionRows:
            for player in playerInfoArray:
                if player.id == row[0]:
                    player.addStintPositionStats(row[1],row[2],row[3],row[4],row[5])            
    
        if db:
            db.close()
   
    return playerInfoArray
    
def calculateLeagueAverages(arr):
    leagueStatsSum = [0]*10
    
    league_avgs = [0]*8
    # loop through all players
    for player in arr:
        # cut off at 600 ab
        if player.total_avgs[1] >= 600:
            for i in range(0,10):
                leagueStatsSum[i] += player.sums[i]
 
    league_avgs[0] = leagueStatsSum[0]  
    league_avgs[1] = leagueStatsSum[1]        
    
    if leagueStatsSum[0] != 0 and leagueStatsSum[1] != 0:
        league_avgs[2] = float(leagueStatsSum[2])/float(leagueStatsSum[0])        
        league_avgs[3] = float(leagueStatsSum[4])/float(leagueStatsSum[0]) 
        league_avgs[4] = float(leagueStatsSum[5])/float(leagueStatsSum[0]) 
        league_avgs[5] = float(leagueStatsSum[6])/float(leagueStatsSum[0]) 
        league_avgs[6] = float(leagueStatsSum[3])/float(leagueStatsSum[1])
        league_avgs[7] = float(leagueStatsSum[3] + leagueStatsSum[7] + leagueStatsSum[8])/float(leagueStatsSum[1] + leagueStatsSum[7] + leagueStatsSum[8] + leagueStatsSum[9])
        
    return league_avgs   
    
def calculateYearlyLeagueAverages(arr, year):
    yearlyLeagueStatsSum = [0]*10    
    yearlyLeagueAvgs = [0]*8
    
    # loop through all players
    for player in arr:
        if year in [k for k,v in player.stats.items()]:
            # cut off at 250 ab
            if player.yavgs[year][1] >= 250:
                for i in range(0,10):
                    yearlyLeagueStatsSum[i] += player.stats[year][i]
 
    yearlyLeagueAvgs[0] = yearlyLeagueStatsSum[0]  
    yearlyLeagueAvgs[1] = yearlyLeagueStatsSum[1]        
    
    if yearlyLeagueStatsSum[0] != 0 and yearlyLeagueStatsSum[1] != 0:
        yearlyLeagueAvgs[2] = float(yearlyLeagueStatsSum[2])/float(yearlyLeagueStatsSum[0])        
        yearlyLeagueAvgs[3] = float(yearlyLeagueStatsSum[4])/float(yearlyLeagueStatsSum[0]) 
        yearlyLeagueAvgs[4] = float(yearlyLeagueStatsSum[5])/float(yearlyLeagueStatsSum[0]) 
        yearlyLeagueAvgs[5] = float(yearlyLeagueStatsSum[6])/float(yearlyLeagueStatsSum[0]) 
        yearlyLeagueAvgs[6] = float(yearlyLeagueStatsSum[3])/float(yearlyLeagueStatsSum[1])
        yearlyLeagueAvgs[7] = float(yearlyLeagueStatsSum[3] + yearlyLeagueStatsSum[7] + yearlyLeagueStatsSum[8])/float(yearlyLeagueStatsSum[1] + yearlyLeagueStatsSum[7] + yearlyLeagueStatsSum[8] + yearlyLeagueStatsSum[9])    
    
    return yearlyLeagueAvgs    

def calculateStdDevs(arr, lavgs):
    significant_players = 0
    squaredValueSum = [0]*6
    std_devs = [0]*6
    for player in arr:
        # cut off at 600 ab
        if player.total_avgs[1] >= 600:
            significant_players += 1
            for i in range(0,6):
                squaredValueSum[i] += math.pow(player.total_avgs[i+2] - lavgs[i+2],2)

    for j in range(0,6):
        std_devs[j] = math.sqrt(float(squaredValueSum[j])/float(significant_players))  
    return std_devs
    
def calculateYearlyStdDevs(arr, year,lavgs):
    significant_players = 0
    squaredValueSum = [0]*6
    std_devs = [0]*6
   
    for player in arr:
        if year in [k for k,v in player.stats.items()]:
            # cut off at 250 ab
            if player.yavgs[year][1] >= 250:
                significant_players += 1
                for i in range(0,6):
                    squaredValueSum[i] += math.pow(player.yavgs[year][i+2] - lavgs[i+2],2)

    for j in range(0,6):
        std_devs[j] = math.sqrt(float(squaredValueSum[j])/float(significant_players))  
    return std_devs

def dumpCSV(playerInfoArray,cats_counted,year_arr):
    cats = ['r','hr','rbi','sb','avg','obp']
    positions = {}
    positions['OF'] = ['LF','CF','RF']
    positions['1B'] = ['1B']
    positions['3B'] = ['3B']
    positions['CI'] = ['1B','3B']
    positions['2B'] = ['2B']
    positions['SS'] = ['SS']
    positions['MI'] = ['2B','SS']
    positions['C'] = ['C']
    positions['P'] = ['P']    
    header = "name,g,ab,"
    catstring = ""
    scorestring = ""
    totalscorestring = ""
    total_header = header
    for i in range(0,len(cats_counted)):
        if cats_counted[i] == 1:
            catstring += cats[i] + ','
            scorestring += cats[i] + "_score,"
            totalscorestring += cats[i] + "_score," + cats[i] + "_trend,"
    
    header += catstring + scorestring +'total_score'
    total_header += catstring + totalscorestring +'total_score,total_trend'
    
    for h in range(0,len(year_arr)):
        year = year_arr[h]
        fo = open('batting_'+str(year) + '.csv',"wb")
        fo.write(header + '\n')
        for i in range(0, len(playerInfoArray)):
            if year in [k for k,v in playerInfoArray[i].stats.items()]:
                if playerInfoArray[i].yavgs[year][1] >= 250:
                    playerString = playerInfoArray[i].first + ' ' + playerInfoArray[i].last+ ','+str(playerInfoArray[i].yavgs[year][0]) + ','+str(playerInfoArray[i].yavgs[year][1]) + ','
                    playerCatString = ''
                    playerScoreString = ''
                    for j in range(0,len(cats_counted)):
                        if cats_counted[j] == 1:
                            playerScoreString += str(playerInfoArray[i].yearlyRawScores[year][j]) + ','
                            if j<4:
                                playerCatString += str(162*playerInfoArray[i].yavgs[year][j+2]) + ','
                            else : 
                                playerCatString += str(playerInfoArray[i].yavgs[year][j+2]) + ','
                    playerString += playerCatString + playerScoreString + str(playerInfoArray[i].yearlyTotalRawScore[year])
                    fo.write(playerString + '\n')
        fo.close()
        
    for h in range(0,len(year_arr)):
        year = year_arr[h]
        fo = open('batting_total.csv',"wb")
        fo.write(total_header + '\n')
        for i in range(0, len(playerInfoArray)):
            if year in [k for k,v in playerInfoArray[i].stats.items()]:
                lastYearSignificant = False
                if year_arr[-1] in [k for k,v in playerInfoArray[i].stats.items()]:
                    if playerInfoArray[i].yavgs[year_arr[-1]][1] >= 250:
                        lastYearSignificant = True
                        
                if playerInfoArray[i].total_avgs[1] >= 600 or (lastYearSignificant):
                    playerString = playerInfoArray[i].first + ' ' + playerInfoArray[i].last+ ','+str(playerInfoArray[i].total_avgs[0]) + ','+str(playerInfoArray[i].total_avgs[1]) + ','
                    playerCatString = ''
                    playerScoreString = ''
                    for j in range(0,len(cats_counted)):
                        if cats_counted[j] == 1:
                            playerScoreString += str(playerInfoArray[i].rawscores[j]) + ','+str(playerInfoArray[i].trendScores[j]) + ','
                            if j<4:
                                playerCatString += str(162*playerInfoArray[i].total_avgs[j+2]) + ','
                            else : 
                                playerCatString += str(playerInfoArray[i].total_avgs[j+2]) + ','
                    playerString += playerCatString + playerScoreString + str(playerInfoArray[i].totalrawscore) + ',' + str(playerInfoArray[i].totalTrendScore)
                    fo.write(playerString + '\n')
        fo.close()        
        #if playerInfoArray[i].total_avgs[1] >= 600:
        #    playerString = playerInfoArray[i].first + ' ' + playerInfoArray[i].last+ ','+str(playerInfoArray[i].total_avgs[0]) + ','+str(playerInfoArray[i].total_avgs[1]) + ','+str(162*playerInfoArray[i].total_avgs[2]) + ','+str(162*playerInfoArray[i].total_avgs[3]) + ','+str(162*playerInfoArray[i].total_avgs[4]) + ','+str(162*playerInfoArray[i].total_avgs[5]) + ','+str(playerInfoArray[i].total_avgs[6]) + ','+str(playerInfoArray[i].total_avgs[7]) + ',' +str(playerInfoArray[i].rawscores[0]) +','+ str(playerInfoArray[i].rawscores[1]) +','+ str(playerInfoArray[i].rawscores[2]) +','+ str(playerInfoArray[i].rawscores[3]) +','+ str(playerInfoArray[i].rawscores[4]) +','+ str(playerInfoArray[i].rawscores[5]) +',' +str(playerInfoArray[i].totalrawscore) 
        #    print playerString
    
    # Create spreadsheet for totals
            
def main():

    # Set up player list and assign by querying database
    playerInfoArray = getStats()
    
    # assume all goals, assists, points, blocks, hits, pim counts
    cats_counted = [1,1,1,1,1,1]
    
    year_arr = [2010,2011,2012]
    
    # Experiment (sort players by hits)
    #playerInfoArray.sort(key=lambda x: x.hits, reverse=True)   
    
    # loop through and compute/add averages to playerinfo
    for player in playerInfoArray:
        player.calculateAverageFantasyStats()
        for year in year_arr:
            player.calculateYearlyAverageStats(year)
        
    # compute league averages for players with more than 20 games played
    league_avgs = calculateLeagueAverages(playerInfoArray)       
    
    # compute standard deviations 
    std_devs = calculateStdDevs(playerInfoArray, league_avgs)
    
    yearlyLeagueAvgs = [None]*len(year_arr)
    yearlyStdDevs = [None]*len(year_arr)
    
    # Compute yearly stuff
    for i in range (0,len(year_arr)):
        yearlyLeagueAvgs[i] = calculateYearlyLeagueAverages(playerInfoArray, year_arr[i])
        yearlyStdDevs[i] = calculateYearlyStdDevs(playerInfoArray,year_arr[i],yearlyLeagueAvgs[i])

    # compute raw scores for each category
    for player in playerInfoArray:
        print player.first, player.last, player.positionsEligible
        player.addTotalRawScores(league_avgs, std_devs)
        player.computeTotalScore(cats_counted)
        for i in range(0,len(year_arr)):
            player.addYearlyRawScores(year_arr[i],yearlyLeagueAvgs[i],yearlyStdDevs[i])
            player.computeYearlyTotalScore(year_arr[i],cats_counted)
        player.calculateTrendScores()
            
    # sort by total scores
    playerInfoArray.sort(key=lambda x : x.totalrawscore,reverse=True)
    
    dumpCSV(playerInfoArray, cats_counted,year_arr)
    
    #print "League Averages (normalized to 162 games): R:" + str(league_avgs[2]*162) + " HR:" + str(league_avgs[3]*162) + " RBI:" + str(league_avgs[4]*162) + " SB:" + str(league_avgs[5]*162) + " AVG:" + str(league_avgs[6]) + " OBP:" + str(league_avgs[7]) 
    #print "League Standard Deviations(normalized to 162 games): R:" + str(std_devs[0]*162) + " HR:" + str(std_devs[1]*162) + " RBI:" + str(std_devs[2]*162) + " SB:" + str(std_devs[3]*162) + " AVG:" + str(std_devs[4]) + " OBP:" + str(std_devs[5]) 
    
    #print ""
    #print "Rankings: "
    #print ""

               
if __name__ == "__main__":
    main()