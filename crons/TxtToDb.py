# script to shift text file data to sqlite db
import sqlite3 as sql
from os.path import isfile
from os import remove

TAG_DB = dict()
txtLocation = input('drop musictags.db: ')
file = open(txtLocation, 'r', encoding='utf-16')
contents = file.read()
exec(contents)
file.close()

if isfile('new.db'):
    remove('new.db')

print(contents)
input('File contents read completed')

con = sql.connect('new.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS song(id integer primary key, location VARCHAR, songname VARCHAR)")
cur.execute("CREATE TABLE IF NOT EXISTS tag(id integer primary key, tagname VARCHAR)")
cur.execute("CREATE TABLE IF NOT EXISTS link(songid integer, tagid integer)")
for track in TAG_DB:
    song = track.split('\\')[-1]
    location = '\\'.join(track.split('\\')[:-1])
    cur.execute('INSERT INTO song(location, songname) values(?, ?)', (location, song))
    con.commit()
    songid = cur.lastrowid
    # print('songId: %d'%songid)
    for tag in TAG_DB[track]:
        cur.execute("SELECT * FROM tag where tagname=?", (tag,))
        tagrec = cur.fetchone()
        if tagrec:
            tagid = tagrec[0]
            linkrec = cur.execute('SELECT * FROM link where songid=? and tagid=?', (songid, tagid))
            if not linkrec:
                cur.execute("INSERT INTO link VALUES(?, ?)", (songid, tagid))
                con.commit()
        else:
            cur.execute("INSERT INTO tag(tagname) values(?)", (tag, ))
            con.commit()
            tagid = cur.lastrowid
            cur.execute("INSERT INTO link VALUES(?, ?)", (songid, tagid))
            con.commit()
cur.execute("SELECT * FROM song")
trackCount = len(cur.fetchall())

con.commit()
con.close()

print('%d tracks added ?'%len(TAG_DB))
print('%d tracks added !'%trackCount)