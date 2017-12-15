import warnings

class ValueWarning(Warning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Color():
    """
    Represents a color.
    Available colorspaces: hsv (channel values 0.0-1.0) and rgb (channel values 0-255)
    """
    
    COLORSPACES = ['hsv', 'rgb']
    
    COLORSPACE_DATA_TYPES = {
        'hsv' : float,
        'rgb'  : int,
    }
    
    CHANNEL_NAMES = [
        'hue',
        'saturation',
        'value',
        'red',
        'green',
        'blue',
    ]
    
    def __init__(self, channels, colorspace):
        """
        channels: a tuple
        colorspace: hsv or rgb
        """
        colorspace = colorspace.lower()
        if colorspace not in self.COLORSPACES:
            raise ValueError('Colorspace must be one of %s.' % self.COLORSPACES)
        self.colorspace = colorspace
        datatype = self.COLORSPACE_DATA_TYPES[colorspace]
        self.channels = [datatype(c) for c in channels]
        if self.channels != channels:
            warnings.warn(ValueWarning("Loss of precision when converting to canonical datatype for colorspace %s." % colorspace))
        
    def __getitem__(self, index):
        return self.channels[index]
        
    def __getattr__(self, channelName):
        """
        Get channel by name/letter.
        """
        channelName = channelName.lower()
        if channelName in self.CHANNEL_NAMES: 
            channelLetter = channelName[0]
        elif len(channelName) == 1:
            channelLetter = channelName
        else:
            raise AttributeError()
            
        if channelLetter not in self.channels: raise AttributeError()
        
        return self[self.colorspace.index(channelLetter)]
        
    def __str__(self):
        if self.COLORSPACE_DATA_TYPES[self.colorspace] is int:
            return '%s { %d %d %d }' % (self.colorspace + self.channels)
        else:
            return '%s { %0.2f %0.2f %0.2f }' % (self.colorspace + self.channels)