# Mixie

## Usage

Configure the script in the system path so it could be called from a shell.  
Use these commands to control your Mixie.

> to cook up a playlist
>
> ```shell
> music
> music [tags] [moretags] [...] [- [subtags] [moresubtags] [...]]
> ```

> to play songs from a search
>
> ```shell
> music play [search query]
> ```  

> to setup your music library with the right song tags
> to manage tracks that got misplaced or reallocated
>
> ```shell
> music rescan
> ```

> to change tags of existing songs in your library
>
> ```shell
> music retag [search_trackname_to_retag]
> ```

> to view all existing tags
>
> ```shell
> music alltags
> ```

## History

* This was a batch file in the beginning, that simply loaded folders in my collection to [VLC](https://www.videolan.org/vlc/)
* Next, a python file tried to do the same thing a bit more intelligently by saving string `tags` into the comment metadata on audio files.  
  These tags are then used to fetch the playlist.  
  This was tedious and prone to errors.  

  The python script was loading the entire playlist to [VLC](https://www.videolan.org/vlc/) in a single command. This introduced constraints as command prompt had a character limit.  
  This issue was solved by letting the script append each track to the playlist one by one.  

  This was still not so convenient because the script had to load up all the songs in the library on startup, that introduced delays.
* The latest version uses a dictionary to map tags and tracks.  
  This is way faster as it only has to load a single dictionary db and does not have to deal with singular file saves.  
  > Using [pickle](https://docs.python.org/3/library/pickle.html) to handle the db saves is a possible option.  
