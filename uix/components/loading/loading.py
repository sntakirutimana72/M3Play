from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from uix.behaviors import ImageSourcePath
from kivy.properties import NumericProperty, ListProperty


Builder.load_string("""
<WTLoading>:
    canvas.before:
        Color:
            rgba: self.back_layer_color
        Ellipse:
            source: self.source
            pos: self.x + self.height * self.pace, self.y + self.height * self.pace
            size: self.width - self.height * self.pace * 2, self.height - self.height * self.pace * 2
    canvas:
        PushMatrix
        Rotate:
            origin: self.center
            angle: self.angle
        Color:
            rgba: self.fore_layer_color
        Line:
            width: self.layer_width
            circle: (self.center_x, self.center_y, self.height * .425, 0, 130)
    canvas.after:
        PopMatrix

    size_hint_x: None
    width: self.height
    icon_name: 'logo.png'
""")


class WTLoading(Widget, ImageSourcePath):
    angle = NumericProperty(0)
    pace = NumericProperty(.2)
    layer_width = NumericProperty(1.1)
    back_layer_color = ListProperty([.4, .4, .4, .7])
    fore_layer_color = ListProperty([0, .2, .5, .6])

    def on_parent(self, *largs):
        if largs[1]:
            Clock.schedule_interval(self._update_angle_, .02)

    def _update_angle_(self, t_frame):
        self.angle -= 5 + t_frame
