# Contributing to Mixie

## Git standards

* Get started by Cloning the repository or creating your own fork of the project  
* Refer below to understand the Mixie architecture  
* Refer the issues section to checkout Pending issues and features  
  `TODO` tags left in code can also show work that is pending  
* Make your changes on a new branch, preferably named `ft_<yourFeature>`  
* Create your Pull Request explaining the changes you've made if it requires an explanation

## Mixie Architecture

* The `Mixie` class handles all central logic.  
* `MixieController` classes contain functionality for users to access Mixie  
  As of now only a CLI Controller exists  
  This controller is passed to the Mixie and FileManager classes so any user interaction required would get directed to the controller.
* `FileManager` is an abstract class that defines methods that control File Access. These include:  
  * Loading DB  
  * Saving DB  
  * Any extra methods you might need to facilitate these actions  
  * A static method that decides the right FileManager to use  
* `MediaManager` is supposed to handle playback and control to media apps.  
  It is under construction  

## Control Flow

* Onload, the `MixieController` is first initialized as the controller requires minimum dependencies to function.  
* Next the `FileManager` and `Mixie` are also initialized and provided with the controller  
  Any user interaction required would be directed to the controller.  
  `FileManager` is designed to be a singleton class and attempts to reinitialize it will return the same singular instance.  
  Initialization of `FileManager` triggers the file checks and DB initialization if it's the first time using `Mixie`.  
  All data are saved to the users root directory: this is for use in windows, *a linux implementation is required*.
* Finally the main method of the Controller is called, this handles all user interaction.

## History

* This was a batch file in the beginning, that simply loaded folders in my collection to [VLC](https://www.videolan.org/vlc/)
* Next, a python file tried to do the same thing a bit more intelligently by saving string `tags` into the comment metadata on audio files.  
  These tags are then used to fetch the playlist.  
  This was tedious and prone to errors.  

  The python script was loading the entire playlist to [VLC](https://www.videolan.org/vlc/) in a single command. This introduced constraints as command prompt had a character limit.  
  This issue was solved by letting the script append each track to the playlist one by one.  

  This was still not so convenient because the script had to load up all the songs in the library on startup, which caused delays.
* The next version used a python dictionary to map tags and tracks.  
  This is way faster as it only has to load a single dictionary db and does not have to deal with singular file saves.  
  The dictionary is saved as a text file. This was not be an optimum strategy but was left as a concern for later.  
  > Using [pickle](https://docs.python.org/3/library/pickle.html) to handle the db saves was also a possible option.  
* The current architecture is more modular, It contains  
  * `FileManager` abstraction to handle db I/O  
  * a dictionary like before to cache all data before transport to file  
  * a Controller that handles all user interaction
  * and the `Mixie` which processes all core logic  

  This helped seperate the logic involved for different concerns  
  Tests were also added to make sure other changes didn't break anything  
  A bat script was also added to compile the python scripts into a single executable  
  