# Contributing to Mixie

## Git standards

* Get started by Cloning the repository or creating your own fork of the project  
* Refer below to understand the Mixie architecture  
* Refer the issues section to checkout Pending issues and features  
* Make your changes on a new branch, preferably named `ft_<yourFeature>`  
* Create your Pull Request explaining the changes you've made if it requires an explanation

## Mixie Architecture

* All of Mixie's code has been written into one single file.  
  While I agree that this is a bad coding practice, I want it to be portable  
  A single file for the program and another one for the data is the cleanest thing I can think of  

* The `Mixie` class handles all logic for processing data.  
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
