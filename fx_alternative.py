#!/usr/bin/python

import sys
import getopt
import urllib
import csv
import pytz

from datetime import datetime
from BeautifulSoup import BeautifulSoup

# Song Data Type
class Song_t(object):
    def __init__(self, id, title, artist):
        self.title = title
        self.artist = artist
        self.id = id

def read_playlist_from_file(file_path):
    "Reads a CSV file into memory"
    local_play_list = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            song = Song_t(datetime.strptime(row[0], '%Y-%m-%d %H:%M'),row[1],row[2])
            local_play_list.append(song)
    return local_play_list

def write_playlist_to_file(file_path, play_list):
    "Write playlist to CSV file"
    with open("fx_alt_play_list.csv", 'wb') as csvfile:
        for song in play_list:
            csvfile.write(song.id.strftime('%Y-%m-%d %H:%M') + "," + song.title + "," + song.artist + "\n")

def main(argv):

    url = "http://fxalternativeradio.com/"
    play_list_csv_file_path = ""
    help_text = "script.py -i <csv_file>"

    if len(argv) < 1:
        print help_text
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv,"hi:",["input="])
    except getopt.GetoptError:
        print help_text
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print help_text
            sys.exit()
        elif opt in ("-i", "--input"):
            play_list_csv_file_path = arg

    play_list = read_playlist_from_file(play_list_csv_file_path)

    html = urllib.urlopen(url).read()
    parsed_html = BeautifulSoup(html)

    now_playing_html = urllib.urlopen(parsed_html.body.find('iframe', attrs={'name':'now_playing'}).get("src")).read()
    parsed_now_playing = BeautifulSoup(now_playing_html)

    for html_song in parsed_now_playing.body.center(attrs={'class':'clearfix'}):

        # Get Current Date Time Stamp for Arizona
        local_dts = datetime.now(pytz.timezone('US/Mountain'))

        # Read song information from html
        try:
            title = html_song("p", attrs={'class':'title'})[0].text
            artist = html_song("p", attrs={'class':'artist'})[0].text
            time_stamp = datetime.strptime(html_song("p", attrs={'class':'time'})[0].text , '%I:%M %p')
        except:
            continue

        # Update the time stamp to that of when the song was played
        local_dts = local_dts.replace(hour=time_stamp.hour, 
                                      minute=time_stamp.minute,
                                      second=0,
                                      microsecond=0)
        # Update time stamp to be UCT and remove time zone information
        uct_dts = local_dts.astimezone(pytz.utc)
        uct_dts = uct_dts.replace(tzinfo=None)

        # Create song with date time stamp as ID
        song = Song_t(uct_dts, artist, title)

        # Check if song has been added already
        for test_song in play_list:
            if test_song.id == uct_dts:
                break
        else:
            # Add the song to the play list
            print(song.id.strftime('%Y-%m-%d %H:%M') + "," +
                  song.title + "," + 
                  song.artist + "\n")
            play_list.append(song)

    write_playlist_to_file(play_list_csv_file_path, play_list)

if __name__ == "__main__":
   main(sys.argv[1:])


