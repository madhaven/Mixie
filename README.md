# Mixie

The mixie project is a script that helps you load songs into a music player (VLC for now).  
Songs in the library are indexed with a tag that the user assigns.  
The user could therefore call Mixie with different tags to include and avoid and Mixie would fetch the songs accordingly.  
The tags and files are saved in a plain text file.  

## Usage

Configure the script in the system path so it could be called from a shell.  
Use these commands to control your Mixie.

> to cook up a playlist
>
> ```shell
> mixie
> mixie [tags] [moretags] [...] [- [subtags] [moresubtags] [...]]
> ```

> to play songs from a search
>
> ```shell
> mixie play [track name]
> ```  

> to setup your mixie library with the right song tags
> to manage tracks that got misplaced or reallocated
>
> ```shell
> mixie scan
> ```

> to change tags of existing songs in your library
>
> ```shell
> mixie retag [search_trackname_to_retag]
> ```

> to view all existing tags
>
> ```shell
> mixie alltags
> ```

## Contribute to Mixie

Visit the [CONTRIBUTING.md](./CONTRIBUTING.md) documentation to learn how to contribute to the project.

## History

* This was a batch file in the beginning, that simply loaded folders in my collection to [VLC](https://www.videolan.org/vlc/)
* Next, a python file tried to do the same thing a bit more intelligently by saving string `tags` into the comment metadata on audio files.  
  These tags are then used to fetch the playlist.  
  This was tedious and prone to errors.  

  The python script was loading the entire playlist to [VLC](https://www.videolan.org/vlc/) in a single command. This introduced constraints as command prompt had a character limit.  
  This issue was solved by letting the script append each track to the playlist one by one.  

  This was still not so convenient because the script had to load up all the songs in the library on startup, that introduced delays.
* The next version used a python dictionary to map tags and tracks.  
  This is way faster as it only has to load a single dictionary db and does not have to deal with singular file saves.  
  The dictionary is saved as a text file. This might not be an optimum strategy but is left as a concern for later.  
  > Using [pickle](https://docs.python.org/3/library/pickle.html) to handle the db saves is a possible option.  
* The current architecture is more modular, It contains  
  * `FileManager` abstraction to handle file I/O  
  * a dictionary like before to cache all data before transport to file  
  * a Controller that handles all user interaction
  * and the `Mixie` which processes all core logic  

  The separate classes help to handle diverse actions while keeping update impact minimal  
