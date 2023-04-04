from abc import abstractmethod


class MediaManager(): # TODO
    '''Handles all interaction to a media player.'''
    QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
    QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue "%s"'
    QUERY_VLC_PREVIEW = 'start /b vlc.exe --playlist-enqueue "%s"'

    def __init__(self):
        '''maintains a state of the player'''
        # call super().__init__() while overriding this init
        self.state = 'nonInitialized'
    
    @abstractmethod
    def previewTrack(self, track):
        raise NotImplementedError # TODO
    
    def __init__(self, *args):
        raise NotImplementedError # TODO