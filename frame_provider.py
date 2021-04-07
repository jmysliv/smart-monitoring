from abc import abstractmethod

class FrameProvider(object):    
    @abstractmethod
    def get_frame(self):
        raise NotImplementedError