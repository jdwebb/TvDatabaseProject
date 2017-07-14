# This script uploads json data from a file and creates and populates an SQLite database with the data.
#
import json
import sqlite3
import datetime
import urllib
import codecs

serviceurl = 'http://api.tvmaze.com/singlesearch/shows?'

conn = sqlite3.connect("showDB.sqlite")
cur = conn.cursor()

# Execute a script , use triple quotes to include spaces and all.
#drop if exists is necessary to run the code more than one time.
cur.executescript('''
DROP TABLE IF EXISTS ShowTable;
DROP TABLE IF EXISTS EpisodeTable;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Network;
DROP TABLE IF EXISTS Rating;

CREATE TABLE ShowTable (
    status      TEXT,
    weight      TEXT,
    updated     TEXT,
    name        TEXT,
    language    TEXT,
    scheduleDay TEXT,
    scheduleTime TEXT,
    url         TEXT,
    imageMed    TEXT,
    imageOrig   TEXT,
    premiered   date,
    summary     TEXT,
    link        TEXT,
    webChannel  TEXT,
    id          INTEGER NOT NULL PRIMARY KEY UNIQUE
);


CREATE TABLE EpisodeTable (
    id          INTEGER NOT NULL UNIQUE,
    name        TEXT,
    airDate     date,
    url         TEXT,
    season      INTEGER,
    
    imageOrig   TEXT,
    episode     INTEGER,
    summary     TEXT,
    airTime     TEXT,
    link        TEXT,
    airStamp    TEXT,
    runTime     TEXT,
    show_id     INTEGER,
    PRIMARY KEY(show_id, id),
    FOREIGN KEY(show_id) REFERENCES showTable(id)
);

CREATE TABLE Genre (
    id     INTEGER,
    genre       TEXT,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES showTable(id)
);

CREATE TABLE Network (
    id          INTEGER,
    networkName TEXT,
    runTime     INTEGER,
    timeZone    TEXT,
    code        TEXT,
    countryName TEXT,
    countryId   INTEGER,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES showTable(id)

);

CREATE TABLE Rating (
    id          INTEGER,
    rating      TEXT,
    thetvdb     TEXT,
    tvrage      TEXT,
    imdb        TEXT,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES showTable(id)
)
''')

count = 0

while True:
    i=0
    show = raw_input('Enter a TV Show: ')
    if len(show) < 1: break
    
    url = serviceurl + urllib.urlencode({"q": show,"embed": "episodes"})
    print 'Retrieving', url
    uh = urllib.urlopen(url)

    data = uh.read()

    try: 
        js = json.loads(str(data))
    except: 
        js = None

#    print json.dumps(js, indent =4)

    try:

        showStatus = js["status"]
        showRating = js["rating"]["average"]
        try:
            showGenre1 = js["genres"][1]
            showGenre2 = js["genres"][2]
            showGenre3 = js["genres"][3]
            showGenre4 = js["genres"][4]
        except IndexError:
            print("Genre overload")

        showWeight = js["weight"]
        showUpdated = js["updated"]
        showName  = js["name"]
        showLang = js["language"]
        showScheduleDay = js["schedule"]["days"][0]
        showScheduleTime = js["schedule"]["time"]
        showUrl = js["url"]
        showImageMed = js["image"]["medium"]
        showImageOrig = js["image"]["original"]

        showExternal1 = js["externals"]["thetvdb"]
        showExternal2 = js["externals"]["tvrage"]
        showExternal3 = js["externals"]["imdb"]
        showPremiered = js["premiered"]
        showSummary = js["summary"]
    #    showPrevEpisode = js["_links"]["previousepisode"]
        showSelfLink = js["_links"]["self"]["href"]
        showWebChannel = js["webChannel"]
        showRunTime = js["runtime"]
        showId = js["id"]
        showTimeZone = js["network"]["country"]["timezone"]
        showCode = js["network"]["country"]["code"]
        showCountryName = js["network"]["country"]["name"]
        showCountryId = js["network"]["id"]
        showNetworkName = js["network"]["name"]
        length = (len(js["_embedded"]["episodes"]))

        for i in range(0,length-1):
            print(i)
            print("Episodes loaded")

            epName = js["_embedded"]["episodes"][i]["name"]
            epAirDate = js["_embedded"]["episodes"][i]["airdate"]
            epUrl = js["_embedded"]["episodes"][i]["url"]
            epSeason  = js["_embedded"]["episodes"][i]["season"]
#            epImgMed  = js["_embedded"]["episodes"][i]["image"]["medium"]
            epImgOrig  = js["_embedded"]["episodes"][i]["image"]["original"]
            epNumber  = js["_embedded"]["episodes"][i]["number"]
            epSummary  = js["_embedded"]["episodes"][i]["summary"]
            epAirTime = js["_embedded"]["episodes"][i]["airtime"]
            epLink = js["_embedded"]["episodes"][i]["_links"]["self"]["href"]
            epAirStamp = js["_embedded"]["episodes"][i]["airstamp"]
            epRunTime = js["_embedded"]["episodes"][i]["runtime"]
            epId = js["_embedded"]["episodes"][i]["id"]
        

            cur.execute('''INSERT OR IGNORE INTO ShowTable (status, weight, updated, name, language, scheduleDay, scheduleTime, url, imageMed, imageOrig, premiered, summary, link, webChannel, id)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (showStatus, showWeight ,showUpdated ,showName ,showLang ,showScheduleDay ,showScheduleTime ,showUrl ,showImageMed ,showImageOrig ,showPremiered ,showSummary ,showSelfLink ,showWebChannel ,showId ,))

            cur.execute('''INSERT OR IGNORE INTO EpisodeTable (id, name, airDate, url, season, imageOrig, episode, summary, airTime, link, airStamp, runTime, show_id)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (epId, epName, epAirDate, epUrl, epSeason, epImgOrig, epNumber, epSummary, epAirTime, epLink, epAirStamp, epRunTime, showId, ))

            cur.execute('''INSERT OR IGNORE INTO Genre (id, genre)
                            VALUES(?,?)''', (showId, showGenre1 , ))

            cur.execute('''INSERT OR IGNORE INTO Network (id, networkName, runTime, timeZone, code, countryName, countryId)
                            VALUES(?,?,?,?,?,?,?)''', (showId, showNetworkName, showRunTime, showTimeZone, showCode, showCountryName, showCountryId, ))

            cur.execute('''INSERT OR IGNORE INTO Rating (id, rating, thetvdb, tvrage, imdb)
                            VALUES(?,?,?,?,?)''', (showId, showRating, showExternal1, showExternal2, showExternal3, ))

            i = i + 1
            conn.commit()
    except TypeError:
        continue

cur.close()

