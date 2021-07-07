import requests
import tweepy
import json
import random
import re
import time


alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
COUNTRIES = ['wx','us','es','it','au','gb','pt','bs','fr','mx','ar']




def get_artist():
    country = random.choice(COUNTRIES)
    artists_call = "https://api.musixmatch.com/ws/1.1/chart.artists.get?format=json&callback=callback&page=1&page_size=100&country=" + country + "&apikey=8b10a0fe777fc7f57c6fa7df8533dc87"
    request = requests.get(artists_call)
    data = request.json()
    artists_list = data['message']['body']['artist_list']
    
    choice = random.choice(artists_list)

    name = choice['artist']['artist_name']
    print(name)

    choice = choice['artist']['artist_id']
    return  choice

def get_album():

    artist_id = get_artist()
    album_call = 'https://api.musixmatch.com/ws/1.1/artist.albums.get?format=json&callback=callback&artist_id='+str(artist_id)+'&page_size=100&page=1&apikey=8b10a0fe777fc7f57c6fa7df8533dc87'
    request = requests.get(album_call)
    data = request.json()
    album_list = data['message']['body']['album_list']
    choice = random.choice(album_list)    
    print(choice['album']['album_name'])
    choice = choice['album']['album_id']

    return choice

def get_track():
    album_id = get_album()
    tracks_call = 'https://api.musixmatch.com/ws/1.1/album.tracks.get?format=json&callback=callback&album_id='+str(album_id)+'&page=1&page_size=100&apikey=8b10a0fe777fc7f57c6fa7df8533dc87'
    request = requests.get(tracks_call)
    data = request.json()
    tracks_list = data['message']['body']['track_list']
    
    choice = random.choice(tracks_list)

    name = choice['track']['track_name']
    artist = choice['track']['artist_name']
    print(name)

    choice = choice['track']['track_id']
    return  choice,name,artist 

def get_lyrics():
    lyrics = None
    
    track_id,name,artist= get_track()
    lyric_call = 'https://api.musixmatch.com/ws/1.1/track.lyrics.get?format=json&callback=callback&track_id=' + str(track_id) +'&apikey=8b10a0fe777fc7f57c6fa7df8533dc87'
    request = requests.get(lyric_call)
    data = request.json()
    lyrics = data['message']['body']['lyrics']['lyrics_body']
    
    
    
    return lyrics,name,artist

def split_into_sentences(text):
    text = " " + text + "  "
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    text = text.replace("\n\n","\n")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences][0]
    sentences = sentences.splitlines()
    sentences = sentences[:-1]
    return sentences

def compose_output(sentences,name,artist):
    header = name + ' - ' + artist + '\n\n' 
    body = ''
    try:
        index = random.randint(0,len(sentences)-5)
        body = sentences[index] +'\n'+ sentences[index+1] +'\n'+ sentences[index+2] +'\n'+ sentences[index+3]
    except:
        body.join(sentences)

    output = header + body
    if header == output:
        return None
    return output


auth = tweepy.OAuthHandler("consumer_key","consumer_secret")
auth.set_access_token("access_token","access_token_secret")

while True:

    tweeted = False

    while not tweeted:

        try:

            lyrics,name,artist = get_lyrics()
            print(lyrics)
            lyrics = split_into_sentences(lyrics)
            print(lyrics)

            output = compose_output(lyrics,name,artist)


            if output is not None and len(output) < 280:
                print(output)


                api = tweepy.API(auth, wait_on_rate_limit=True,
                    wait_on_rate_limit_notify=True)
                api.update_status(output)
                tweeted = True
                time.sleep(2700)
            
        except Exception:
            tweeted = False