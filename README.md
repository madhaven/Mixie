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

## How to Build

Mixie uses the library `pyinstaller` to build the python code into an executable  
Run the `build.bat` script to build the script.

## Contribute to Mixie

Visit the [CONTRIBUTING.md](./CONTRIBUTING.md) documentation to learn how to contribute to the project.
