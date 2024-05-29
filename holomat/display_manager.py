import os
from screeninfo import get_monitors

class DisplayManager:
    """
    DisplayManager class initializes and manages display settings.
    """

    def __init__(self):
        """
        Initialize DisplayManager with monitor information and set up display.
        """
        self.monitors = get_monitors()
        self.screen_width, self.screen_height = self._setup_display()

    def _setup_display(self):
        """
        Set up display on the second monitor if available, otherwise on the primary monitor.
        """
        # Set the position and size to the second monitor if it exists
        if len(self.monitors) > 1:
            primary_display_width = self.monitors[0].width
            screen_width = self.monitors[1].width
            screen_height = self.monitors[1].height
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{primary_display_width},0'
        else:
            screen_width = self.monitors[0].width
            screen_height = self.monitors[0].height
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        
        return screen_width, screen_height

    def get_screen_dimensions(self):
        """
        Get the dimensions of the screen.
        """
        return self.screen_width, self.screen_height
