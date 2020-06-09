__all__ = ('CloseBTComponent', 'MinimizeBTComponent', 'ResizeBTComponent', )

from kivy.lang import Builder
from uix.components.buttons import BTComponent
from kivy.properties import ListProperty, NumericProperty


Builder.load_string("""
<CloseBTComponent>:
    canvas:
        PushMatrix
        Color:
            rgba: (*root.graffiti_color, root.toggle_graffiti)
        Rotate:
            angle: root.angle
            origin: self.center
        SmoothLine:
            width: root.graffiti_width
            points: [self.center_x, self.y + dp(4), \
                self.center_x, self.top - dp(4)]
        SmoothLine:
            width: root.graffiti_width
            points: [self.x + dp(4), self.center_y, \
                self.right - dp(4), self.center_y]
    canvas.after:
        PopMatrix
            
            
<ResizeBTComponent>:
    canvas:
        Color:
            rgba: (*root.graffiti_color, root.toggle_graffiti)
        Line:
            width: root.graffiti_width
            rectangle: (self.center_x - dp(4.5), self.center_y - dp(4.5), dp(9), dp(9))


<MinimizeBTComponent>:
    canvas:
        Color:
            rgba: (*root.graffiti_color, root.toggle_graffiti)
        SmoothLine:
            width: root.graffiti_width
            points: (self.center_x - dp(5), self.center_y, self.center_x + dp(5), self.center_y)
""")


class BTComponent(BTComponent):
    hover_color = [1, 1, .6, .1]
    toggle_graffiti = NumericProperty(0)
    graffiti_width = NumericProperty(1.2)
    graffiti_color = ListProperty([0, 0, .1])
    background_color = ListProperty([0, 0, 0, 0])

    def on_hover(self):
        self.__update_feature__()

    def on_leave(self):
        self.__update_feature__()

    def __update_feature__(self):
        self.background_color, self.hover_color = (
            self.hover_color, self.background_color
        )


class CloseBTComponent(BTComponent):
    angle = NumericProperty(45)
    hover_color = [.5, 0, 0, 1]


class ResizeBTComponent(BTComponent):
    pace = NumericProperty(5)


class MinimizeBTComponent(BTComponent):
    pass
