__all__ = ('ProgressBarComponent', )

from kivy.lang import Builder
from uix.components.layers import BLayout
from uix.components.behaviors import ImageSourcePath
from kivy.properties import NumericProperty, ListProperty


Builder.load_string("""
<ProgressBarComponent>:
    icon_name: 'handle_image.png'
    padding: self.height * .5, self.height * self.thick_pace

    canvas:
        # Drawing Floor-Base Object
        Color:
            rgba: self.cover_color
        RoundedRectangle:
            radius: [2]
            pos: self.x, self.y + self.padding[1]
            size: self.width, self.size[1] - self.padding[1] * 2

        ############## Drawing Status Premise ########
        Color:
            rgba: self.progress_color
        RoundedRectangle:
            radius: [2]
            pos: self.x, self.y + self.padding[1]
            size: self.sizer, self.size[1] - self.padding[1] * 2

        # Drawing Handle Object
        Color:
            rgba: self.handle_color
        Rectangle:
            source: self.source
            pos: self.x + self.sizer - self.padding[0], self.y
            size: self.height, self.height
""")


class ProgressBarComponent(BLayout, ImageSourcePath):
    sizer = NumericProperty(0)
    value_ratio = NumericProperty(0.)  # This get to be used in case of any resize trigger

    thick_pace = NumericProperty(.4)
    handle_color = ListProperty([.2, .2, .1, 0])
    cover_color = ListProperty([.05, .03, .03, 0])
    progress_color = ListProperty([.05, .05, .15, .6])

    __events__ = ('on_calculate_sizer', 'on_seek', )

    def on_size(self, *_):
        if self.value_ratio is not None:
            sizer = self.size[0] * self.value_ratio
            self._compute_sizer_and_ratio(sizer=sizer)

    def on_seek(self, *_):
        pass

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            return True
        return super(ProgressBarComponent, self).on_touch_down(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_seek', self._compute_ratio(touch.x - self.x))
            self.dispatch('on_calculate_sizer', touch.x)
            touch.grab(self)
            return True
        return super(ProgressBarComponent, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.dispatch('on_seek', self._compute_ratio(touch.x - self.x))
            self.dispatch('on_calculate_sizer', touch.x)
            return True
        return super(ProgressBarComponent, self).on_touch_down(touch)

    def _compute_ratio(self, sizer):
        return sizer / max(self.size[0], 10e-24)

    def on_calculate_sizer(self, touch_x):
        sizer = touch_x - self.x
        self._compute_sizer_and_ratio(sizer=sizer)

    def calculate_from_ratio(self, ratio):
        sizer = self.size[0] * ratio
        self._compute_sizer_and_ratio(sizer=sizer)

    def _compute_sizer_and_ratio(self, sizer):
        if sizer <= 0:
            sizer = 10e-24
        elif sizer > self.width:
            sizer = self.width

        self.sizer = sizer
        self.value_ratio = self._compute_ratio(sizer)
