from kivy.config import Config
Config.set('graphics', 'borderless', 1)

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.uix.scrollview import ScrollView
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import (
  ListProperty, OptionProperty, BooleanProperty,
  ObjectProperty, NumericProperty, StringProperty
)
from configparser import ConfigParser
from threading import Thread
import json, pyautogui as pyauto
import re, asyncio, sys, time
from os import path, listdir


SETTINGS = None


def startUp_window_size():
  window = json.loads(SETTINGS.get('window', 'window'))
  Window.size = window.get('window-size')


def startUp_window_pos():
  window = json.loads(SETTINGS.get('window', 'window'))
  Window.left, Window.top = window.get('window-pos')


def load_setting_onStartUp():
  global SETTINGS
  SETTINGS = ConfigParser()
  SETTINGS.read('settings.ini')

  Window.minimum_width = 450
  Window.minimum_height = 68

  startUp_window_size()


def getProperty(prop_name):
  try:
    property_parts = prop_name.split(' ')
    section = property_parts[0]
    prop = property_parts[1]
    key = property_parts[2]
    property = json.loads(SETTINGS.get(section, prop))
    return property.get(key)
  except Exception as error:
    Logger.critical("SYAI3Play:~CONFIG::%s" % error)


load_setting_onStartUp()

Builder.load_string('''
<MainRoot>:
    orientation: 'vertical'
    normal: root.getProperty('custom body bkg-color')
    outl_w: root.getProperty('custom body border-width')
    outl_clr: root.getProperty('custom body border-color')

    HeadBar:
        id: head_bar
        size_hint_y: None
        height: dp(30)
    # body-div
    ScreenManager:
        id: disp_manager
        Screen:
            name: '3player'
            id: play3_screen

            # main child of the screen widget
            BoxLayout:
                id: msc_cont

                # right nav container of player GUIs
                Play3:
                    id: play3GUIs


<HeadBar>:
    rows: 1
    spacing: '10sp'
    normal: root.getProperty('custom title bkg-color')
    GridLayout:
        minimum_width: dp(120)
        padding: 6
        rows: 1

        # Logo-Image
        CustomButton:
            hoverClr: ()
            size_hint_x: None
            width: self.height
            source: root.getProperty("custom title logo-image")

        # Application-Name
        Label:
            shorten: True
            valign: "middle"
            text: 'SYAI3Play'
            text_size: self.size
            font_size: min(*self.size) // 2 + 1 \
                if not (min(*self.size) // 2) % 2 \
                else min(*self.size) // 2 + 2
            font_name: root.getProperty("custom title font-name")
            color: root.getProperty("custom title font-color")

    # Player PosterOffice and must be of 2 children widgets at least
    BoxLayout:
        id: posterOffice
        padding: (0, 6)
        spacing: '4sp'
        size_hint_x: None
        width: dp(360) if root.size[0] > 550 else dp(230)

        AutoRollLabel:
            text: root.currentPlaylist
        CustomButton:
            size_hint_x: None
            width: dp(self.height + 2)
            source: './Icons/more.png'
            on_down: root._revealMoreOptions()

    # Window function buttons
    GridLayer:
        size_hint_x: None
        width: dp(72)
        padding: 7
        spacing: 5
        rows: 1
        WindowCtrls:
            on_down: root.do_resize()
            source: './Icons/green.png'
        WindowCtrls:
            on_down: root.do_minimize()
            source: './Icons/yellow.png'
        WindowCtrls:
            on_down: root.do_terminate()
            source: './Icons/red.png'


<LeftNavMenu>:
    size_hint_x: None
    splitter: splitter.__self__
    ScrollInactiveBar:
        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height

            PlaylistManager:
                id: playlists
                grand_parent: root.__self__
            StreamsManager:
                id: streams
                grand_parent: root.__self__
            DownloadManager:
                id: downloads
                grand_parent: root.__self__
            FavoriteManager:
                id: favorites
                grand_parent: root.__self__


    CustomButton:
        id: splitter
        radius: [0]
        size_hint_x: None
        width: root.strip_size
        h_normal: root.strip_hoverClr
        hoverClr: root.strip_hoverClr
        source: root.strip_backgroundImg
        normal: root.strip_backgroundClr


<Play3>:
    orientation: 'vertical'
    # playlist nav
    FloatLayout:
        size_hint_y: None
        height: dp(root.height - 98) if root.height > 98 else 0
        CustomButton:
            normal: (0, 0, 0, 0) if self.size[1] < 10 else (.4, .4, .6, 1)
            pos: self.parent.pos
            pos_hint: {'center_y': .5, 'center_x': .5}
            source: './Icons/thumbnail.png'
            hoverClr: ()
            size_hint: (None, None)
            height: dp(150) \
              if self.parent.height > 150 \
              else dp(self.parent.height / 1.2)
            width: self.height
            radius: [0]

    # player control view
    BoxLayout:
        orientation: 'vertical'
        # controls-row1
        BoxLayout:
            id: row_1
            size_hint_y: None
            height: dp(38)
            spacing: '4sp'
            padding: (15, 8)

            PlayerCtrlButton:
                source: './Icons/stop.png'
                on_down: root.stop_playback()
            PlayerCtrlButton:
                id: pp
                source: './Icons/play.png'
                on_touch_down: self.bind(on_down=root.play_pause)
            PlayerCtrlButton:
                source: './Icons/preview.png'
                on_down: root._previous()
            PlayerCtrlButton:
                source: './Icons/rewind.png'
                on_down: root.backward_wind()

            # Volume control
            FloatLayout:
                id: vol_cont
                padding: (5, 0)
                VolumeBar:
                    pos: self.parent.pos
                    pos_hint: {'center_y': .5}
                    size_hint_y: None
                    height: dp(4)
                    id: volTuner
            PlayerCtrlButton:
                source: './Icons/wind.png'
                on_down: root.forward_wind()
            PlayerCtrlButton:
                source: './Icons/next.png'
                on_down: root._next()
            PlayerCtrlButton:
                id: shufflee
                source: './Icons/shuffle-off.png'
                on_touch_down: self.bind(on_down=root._shuffle_alter)
            PlayerCtrlButton:
                id: loope
                source: './Icons/repeat-off.png'
                on_touch_down: self.bind(on_down=root._loop_alter)

        # controls-row2
        BoxLayout:
            id: row_2
            orientation: 'vertical'
            size_hint_y: None
            height: dp(60)
            spacing: '6sp'
            padding: (15, 3)

            BoxLayout:
                spacing: '5sp'
                # Volume Level
                StatusDisplayLabel:
                    display_type: 'vol'
                    width: dp(70)
                    textVal: '{:.1f}'.format(root.volume * 100)
                # Media Format
                StatusDisplayLabel:
                    display_type: 'format'
                    width: dp(75)
                    textVal: ' '
                    id: track_format
                # Media State
                StatusDisplayLabel:
                    display_type: 'state'
                    width: dp(75)
                    textVal: ' ' if root.state == 'stop' else root.state
                # Media Name
                AutoRollLabel:
                    font_size: '10sp'
                    text: 'No track'
                    autoScroll: True
                    id: track_name
            BoxLayout:
                spacing: '12sp'

                # Elapsed Time
                MediaTimeCounter:
                    text: ''
                    id: time_lap
                FloatLayout:
                    id: progress_cont
                    HrzProgressBar:
                        id: mediaPos
                        level_normal: [1, 1, 0, .2]
                        pos: self.parent.pos
                        pos_hint: {'center_y': .5}
                        bar_active: False
                        size_hint_y: None
                        height: dp(4)
                # Estimated Duration
                MediaTimeCounter:
                    text: ''
                    id: time_estimate
            Label:
                size_hint_y: None
                height: dp(10)


<PlayerCtrlButton@CustomButton>:
    size_hint_x: None
    width: dp(self.size[1] + 1)


<AutoRollLabel>:
    HoverableLabel:
        text: root.text
        valign: 'middle'
        halign: 'center'
        color: root.color
        size_hint_x: None
        font_size: root.font_size
        text_size: (None, self.size[1])
        width: self.texture_size[0]
        on_enter: root.on_enter()
        on_leave: root.on_leave()


<WindowCtrls>:
    canvas:
        Color:
            rgba: self.normal
        Ellipse:
            pos: self.pos
            size: self.size
            source: self.source


<MoreOptions>:
    normal: (.12, .12, .15, 1)
    pos_hint: {'top': 1}
    size_hint_y: None
    height: dp(38)

    BoxLayer:
        spacing: '4sp'
        normal: (1, .3, 1, .02)
        padding: ((self.width - 390) * .5, 5)

        # DOCK
        CustomButton:
            on_down: root.root.on_miniDockSwitch('dock')
            normal: (1, .8, 1, .07)
            size_hint_x: None
            width: dp(50)
            text: 'dock'
        # SETTINGS
        CustomButton:
            normal: (1, .8, 1, .07)
            size_hint_x: None
            text: 'settings'
            width: dp(70)
        # MINIMAL
        CustomButton:
            on_down: root.root.on_miniDockSwitch('mini')
            normal: (1, .8, 1, .07)
            size_hint_x: None
            width: dp(70)
            text: 'minimal'

        # SearchBox
        BoxLayer:
            normal: (.15, .15, .15, 1)
            radius: [4]
            InputField:
                text: 'Find and play'
            CustomButton:
                size_hint_x: None
                width: self.height
                h_normal: (1, 0, 0, .1)
                radius: [0, 5, 5, 0]
                source: './Icons/search.png'


<HrzProgressBar>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius

        Color:
            rgba: self.level_normal
        RoundedRectangle:
            pos: self.pos
            size: (self.progressLevel, self.size[1])
            radius: self.radius

        Color:
            rgba: self.handler_normal
        Ellipse:
            pos: (self.pos[0] + self.progressLevel - 7.5, self.pos[1] - (15 - self.height) / 2)
            size: (15, 15)
            source: self.handler_image


<MediaTimeCounter>:
    size_hint_x: None
    text_size: (None, self.size[1])
    width: self.texture_size[0]


<StatusDisplayLabel>:
    size_hint_x: None
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            radius: self.radius
            pos: self.pos
            size: self.size


<PlaylistCtrlButton@CustomButton>:
    size_hint_x: None
    width: dp(50)
    spared: 0
    color: (0, 0, 0, 1)
    normal: (0, 0, 0, 0)


<NavElement>:
    cols: 1
    size_hint_y: None
    height: max(dp(28), self.compute_height())
    HoverableLabel:
        id: head_title
        canvas.before:
            Color:
                rgb: (1, 1, 1)
            Rectangle:
                pos: self.x + 8, self.y + 2
                size: (24, 24)
                source: root.source
            Color:
                rgba: root.normal if not self.hovered else root.selected_normal
            Rectangle:
                pos: self.pos
                size: self.size
        text: root.title
        color: root.color
        font_name: root.font_name
        font_size: root.font_size
        size_hint_y: None
        valign: 'middle'
        height: dp(28)
        text_size: self.size[0] - dp(80), self.height


<SinglePlaylist>:
    contents: playlist_content.__self__
    height: dp(28) \
        if not self.contents.parent \
        else dp(28 + self.contents.height)
    BoxLayout:
        id: playlist_content
        size_hint_y: None
        height: 0 if not play_list.children else min(dp(200), play_list.height)
        ScrollInactiveBar:
            PlayItemManager:
                cols: 1
                id: play_list
                spacing: "2sp"
                size_hint_y: None
                height: self.minimum_height


<PlaylistManager>:
    title: 'Playlists'
    contents: playlists_content.__self__
    height: dp(28) \
        if not self.contents.parent \
        else dp(28 + self.contents.height)
    GridLayout:
        cols: 1
        id: playlists_content
        size_hint_y: None
        height: dp(50)
        StackLayout:
            orientation: 'tb-rl'
            padding: (0, 2)
            size_hint_y: None
            height: dp(22)
            id: head_menu
            PlaylistCtrlButton:
                text: 'Delete'
                radius: [0, 3, 3, 0]
                h_normal: (1, 0, 0, .6)
                font_name: "LiberationMono-Regular"
                disabled: root.enablePlaylistDelete
                on_down: root._delete_playlist()
            PlaylistCtrlButton:
                radius: [0]
                text: 'Rename'
                h_normal: (1, .76, .8, .6)
                font_name: "LiberationMono-Regular"
                disabled: root.enablePlaylistRename
                on_down: root._rename_playlist()
            PlaylistCtrlButton:
                text: 'New'
                radius: [3, 0, 0, 3]
                h_normal: (0, 1, 0, .6)
                font_name: "LiberationMono-Regular"
                on_down: root._create_playlist()


<StreamsManager>:
    title: 'Streams'

<DownloadManager>:
    title: 'Downloads'

<FavoriteManager>:
    title: 'Favorites'


<LoadingStatus>:
    Label:
        text: root.message
        font_size: "10sp"
        color: (.6, .2, .8, 1)
        font_name: "Trebuchet_MS_Italic"
    Loading:
        size_hint_x: None
        width: self.height


<CustomButton>:
    canvas.before:
        Color:
            rgba: self.h_normal
        RoundedRectangle:
            radius: self.radius
            pos: self.pos
            size: self.size
        Color:
            rgba: self.normal
        Rectangle:
            source: self.source
            pos: (self.pos[0] + (self.spared / 2), self.pos[1] + (self.spared / 2))
            size: (self.size[0] - self.spared, self.size[1] - self.spared)


<GridLayer>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius


<BoxLayer>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius
    canvas:
        Color:
            rgba: self.outl_clr
        Line:
            width: self.outl_w
            rounded_rectangle: (*self.pos, *self.size, *self.outl_r)


<Loading>:
    canvas:
        Color:
            rgba: (.6, 1, 1, .05)
        Line:
            width: 1.1
            ellipse: (self.center_x - self.size[1] / 2, \
                    self.pos[1], self.size[1], self.size[1])
        PushMatrix
        Rotate:
            origin: self.center
            angle: self.angle
            axis: (0, 0, 1)
        Color:
            rgba: (1, .6, 1, .1)
        Line:
            width: 1.01
            ellipse: (self.center_x - self.size[1] / 2, \
                      self.pos[1], self.size[1], self.size[1], 0, 95)
        PopMatrix


<PlayItem>:
    size_hint_y: None
    height: dp(24)
    shorten: True
    valign: 'middle'
    font_size: '10sp'
    color: [.35, .35, .3, 1]
    font_name: 'RobotoMono-Regular'
    text_size: self.size[0] - dp(60), self.height
    canvas.before:
        Color:
            rgb: (1, 1, 1)
        Rectangle:
            pos: self.x + 6, self.y + 4
            size: (16, 16)
            source: self.source
        Color:
            rgba: self.normal if not self.selected else self.selected_normal
        Rectangle:
            pos: self.pos
            size: self.size
''')


class Loading(Label):
  angle = NumericProperty(0)
  name = StringProperty(None)

  def __init__(self, **kwargs):
    super(Loading, self).__init__(**kwargs)
    Clock.schedule_interval(self._update_angle, 0)

  def _update_angle(self, dt):
    self.angle -= 9

  def on_parent(self, *largs):
    if not largs[1]:
      Clock.unschedule(self._update_angle)


class MediaTimeCounter(Label):
  '''
  :class:inherits from :class:`kivy.uix.label`
  ..value::`Created to display elapsed and estimated time
      while the player is functioning
  '''
  time_stamp = NumericProperty(None, allownone=True)
  '''A container for time stamp to rationalize
     :attr: is a :class:`kivy.properties` and default to None

     ..Warning::`Only decimal or real number are accepted
  '''
  font_name = 'RobotoMono-Regular'
  color = [.2, .2, .2, 1]
  font_size = 11

  def on_time_stamp(self, *largs):
    if largs[1] is None:
      rationTime = ''
    else:
      hours = largs[1] // 3600
      minutes = (largs[1] % 3600) // 60
      seconds = (largs[1] % 3600) % 60

      if hours == 0.:
        rationTime = '{:02.0f}:{:02.0f}'.format(minutes, seconds)
      else:
        rationTime = '{:.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)
    self.text = rationTime


class StatusDisplayLabel(Label):
  normal = ListProperty([1, 1, 0, .02])
  radius = ListProperty([2])

  display_type = OptionProperty(
    'none', options=['none', 'vol', 'format', 'state'])
  '''Remarks the such type should the assign text value presents

    :attr: is a :class:`kivy.properties` and default to `none`
    ..Warning:: ony accepts of the its options values
  '''
  textVal = StringProperty('')
  '''Temporal container for text value for reformatting with its type

      :attr: is a :class:`kivy.properties` and default to ''
    '''
  font_name = 'RobotoMono-Regular'
  color = [0, 1, 1, 1]
  font_size = 9
  markup = True

  def on_textVal(self, *largs):
    if not largs[1]:
      return
    if self.display_type == 'vol':
      val = 'vol ' + largs[1] + ' [color=#f00]%[/color]'
    elif self.display_type == 'format':
      val = 'format: ' + largs[1]
    elif self.display_type == 'state':
      val = 'status: ' + largs[1]

    self.text = val
    self.textVal = ''


class Hoverable(object):
  hovered = BooleanProperty(False)
  hover_pos = ListProperty([0, 0])

  def __init__(self, **kwargs):
    self.register_event_type('on_enter')
    self.register_event_type('on_leave')
    Window.bind(mouse_pos=self.on_mouse_pos)
    super(Hoverable, self).__init__(**kwargs)

  def on_mouse_pos(self, *largs):
    if not self.get_root_window():
      return

    pos = largs[1]
    inside = self.collide_point(*self.to_widget(*pos))
    if self.hovered == inside:
      return
    self.hovered = inside

    if inside:
      self.hover_pos = pos
      self.dispatch('on_enter')
    else:
      self.dispatch('on_leave')

  def on_enter(self):
    pass

  def on_leave(self):
    pass


class HoverWidget(Widget, Hoverable):
  pass


class HoverableLabel(Label, HoverWidget):
  font_size = NumericProperty('11sp')
  color = ListProperty([.4, .4, .3, 1])
  font_name = StringProperty('RobotoMono-Regular')


class MyButton(Widget):
  def __init__(self, **kwargs):
    self.register_event_type('on_up')
    self.register_event_type('on_down')
    super(MyButton, self).__init__(**kwargs)

  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      self.dispatch('on_down')
      return True
    return super(MyButton, self).on_touch_down(touch)

  def on_touch_up(self, touch):
    if self.collide_point(*touch.pos):
      self.dispatch('on_up')
      return True
    return super(MyButton, self).on_touch_up(touch)

  def on_up(self):
    pass

  def on_down(self):
    pass


class ScrollInactiveBar(ScrollView):
  bar_color = ListProperty([0, 0, 0, 0])
  bar_inactive_color = ListProperty([0, 0, 0, 0])
  effect_cls = ObjectProperty(OpacityScrollEffect)


class GridLayer(GridLayout):
  radius = ListProperty([0])
  normal = ListProperty([0, 0, 0, 0])


class BoxLayer(BoxLayout):
  radius = ListProperty([0])
  outl_r = ListProperty([0])
  outl_w = NumericProperty(1)
  normal = ListProperty([0, 0, 0, 0])
  outl_clr = ListProperty([0, 0, 0, 0])


class HandleChildrenFocus(Widget):
  new_focused = ObjectProperty(None, allownone=True)
  ''' contains the new selected child
  :attr:`focused` is a :class:`~kivy.properties.ObjectProperty` and
      default to None
  '''
  current_focused = ObjectProperty(None, allownone=True)
  ''' contains the currently selected child
  :attr:`focused` is a :class:`~kivy.properties.ObjectProperty` and
      default to None
  '''

  def on_new_focused(self, *largs):
    pass


class LeftNavMenu(BoxLayer):
  focused = None

  strip_size = NumericProperty(6)
  '''width size value for the splitter
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 6
  '''
  strip_backgroundImg = StringProperty('')
  '''splitter background image if preferred
    :attr: is a :class:`~kivy.properties.StringProperty` and default to ''
  '''
  strip_backgroundClr = ListProperty([.3, .3, .4, .3])
  '''splitter background color
    :attr: is a :class:`~kivy.properties.ListProperty` and default to [.8, .8, 1, .05]
  '''
  strip_hoverClr = ListProperty([.6, .6, 1, .1])
  '''splitter hover background color
    :attr: is a :class:`~kivy.properties.ListProperty` and default to [0, 1, 1, .01]
  '''
  min_size = NumericProperty(200)
  '''self size that the splitter cannot go pass while decreasing size and also
      it's the default self size
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 200
  '''
  max_size = NumericProperty(200)
  '''self size that the splitter cannot go pass while increasing size
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 200
  '''
  splitter = ObjectProperty(None)
  '''a splitter widget
    :attr: is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''

  def __init__(self, **kwargs):
    self.register_event_type('on_split_size')
    super(LeftNavMenu, self).__init__(**kwargs)
    self.normal = json.loads(SETTINGS.get('leftNav', 'background_color'))
    self.width = self.min_size
    if self.min_size > self.max_size:
      self.min_size = self.max_size

  def alter_focus(self, focus):
    if self.focused:
      if self.focused is focus:
        self.focused = None
        return
      self.focused.alter_selection()
    self.focused = focus

  def on_touch_down(self, touch):
    if self.splitter.collide_point(*touch.pos):
      touch.grab(self)
      self.dispatch('on_split_size', touch.pos[0])
      return True
    return super(LeftNavMenu, self).on_touch_down(touch)

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self.dispatch('on_split_size', touch.pos[0])
    return True

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      touch.ungrab(self)
    return True

  def on_split_size(self, pos_x):
    new_width = pos_x - self.pos[0]
    if self.min_size <= new_width <= self.max_size:
      self.width = new_width

  def on_max_size(self, *largs):
    self.normalize_max_size()

  def on_parent(self, *largs):
    if not largs[1]:
      self.width = self.min_size

  def normalize_max_size(self):
    if self.width > self.max_size:
      self.width = self.max_size


class NavElement(GridLayout):
  grand_parent = ObjectProperty(None)
  contents = ObjectProperty(None)
  is_open = BooleanProperty(False)
  selected = BooleanProperty(None)

  source = StringProperty('')
  font_size = NumericProperty('11sp')
  normal = ListProperty([0, 0, 0, 0])
  color = ListProperty([.6, 1, .6, 1])
  title = StringProperty('Element title')
  selected_normal = ListProperty([.6, .7, 1, .05])
  font_name = StringProperty('RobotoMono-Regular')

  def __init__(self, **kwargs):
    self.register_event_type('on_collapse_expand')
    super(NavElement, self).__init__(**kwargs)

  def on_parent(self, *largs):
    if largs[1]:
      self.decide_on_contents()

  def on_touch_down(self, touch):
    if self.ids.head_title.collide_point(*touch.pos):
      self.dispatch('on_collapse_expand')
      return True
    return super(NavElement, self).on_touch_down(touch)

  def on_collapse_expand(self):
    if self.contents:
      self.alter_selection()
      if self.grand_parent:
        self.grand_parent.alter_focus(self)

  def alter_selection(self):
    self.selected = not self.selected

  def decide_on_contents(self, *largs):
    if self.is_open:
      if not (self.ids and self.contents):
        Clock.schedule_once(self.decide_on_contents, .2)
      else:
        self.unbind(selected=self.on_selected)
        self.selected = True
        self.on_selected('', 1)
        self.bind(selected=self.on_selected)
    else:
      if not (self.ids and self.contents):
        Clock.schedule_once(self.decide_on_contents, .2)
      else:
        self.selected = False

  def on_selected(self, *largs):
    if not self.contents:
      return

    if largs[1]:
      if largs[1] is True:
        self.add_widget(self.contents)
      self.normal = [1, 1, .6, .05]
    else:
      self.remove_widget(self.contents)
      self.normal = [0, 0, 0, 0]
    self.is_open = not self.is_open

  def compute_height(self):
    return 25 if not self.contents else (26 + self.contents.size[1])


class SinglePlaylist(NavElement):
  source = './Icons/playlist2.png'

  def on_selected(self, *largs):
    super().on_selected(*largs)
    if largs[1] and self.grand_parent.is_viable_to_change_activePlaylist():
      self.grand_parent.activePlaylist = self.title


class PlaylistManager(NavElement):
  focused = None
  source = './Icons/playlist.png'

  playlistOldTitle = None
  enablePlaylistDelete = BooleanProperty(True)
  '''Used to enable and disable a button of deleting a playlist
      if True the deleting button is disabled otherwise is enabled
  :attr:`enablePlaylistDelete` is a :class:`~kivy.properties.BooleanProperty` and
                                                default to True
  '''
  enablePlaylistRename = BooleanProperty(True)
  '''Used to enable and disable a button of renaming a playlist
      if True the renaming button is disabled otherwise is enabled
  :attr:`enablePlaylistRename` is a :class:`~kivy.properties.BooleanProperty` and
                                                default to True
  '''
  activePlaylist = StringProperty('')
  '''A reference object-id-name to the being used playlist. Mostly the playlist being played
      is the active one but if there is none being played, the active one is activated
          by a double click
  :attr:`activePlaylist` is a :class:`~kivy.properties.StringProperty` and default to ''
  '''
  savingQueue = None
  '''Used to hold all new playlists to be saved
  :attr:`pendingQueue` is a :class:`~python.dict` and default to None
  '''
  savingState = None
  '''used to indicate that the saving process has been initiated
  :attr:`unloadingState` is a :class:`~python.bool` and default to None
  '''
  pendingQueue = None
  '''Used to hold an new coming in lists temporarily in case there is one already in progress
  :attr:`pendingQueue` is a :class:`~python.dict` and default to None
  '''
  unloadingState = None
  '''used to prevent more than one queue to enter unloading process at the same time
  :attr:`unloadingState` is a :class:`~python.bool` and default to None
  '''
  unloadingQueue = None
  ''' Used to hold an active load queue data
  :attr:`unloadingQueue` is a :class:`~python.list` and default to None
  '''

  def alter_focus(self, focus):
    if self.focused:
      if self.focused is focus:
        self.focused = None
        self.contents.size[1] -= 228
        self.enable_functionality(False)
        return
      self.focused.alter_selection()
    else:
      self.contents.size[1] += 228
    self.focused = focus
    self.enable_functionality(True)

  @staticmethod
  def is_viable_to_change_activePlaylist():
    root = App.get_running_app().root
    return root.ids.play3GUIs.is_ready(True)

  def on_activePlaylist(self, *largs):
    root = App.get_running_app().root
    root.ids.head_bar.currentPlaylist = largs[1]

  def _decisionOn_newList(self, new_list):
    # checking if the activePlaylist is a NoneType
    active_name = 'unnamed playlist' if not self.activePlaylist else self.activePlaylist
    # trigger playlist save in a local file to be reused later on when needed
    self.trigger_playlist_save_mode(new_list, active_name)
    # checking if there's no active un-listing progress
    if self.unloadingState:
      # checking if pendingQueue is a NoneType
      if self.pendingQueue is None:
        self.pendingQueue = []
      # storing the new_list to a waiting list
      new_queue = {active_name: new_list}
      self.pendingQueue.append(new_queue)
    else:
      # activating unloading progress
      self.unloadingState = True
      # charge or load queue
      self.unloadingQueue = new_list
      # directive for adding new_list items to a widget
      self.init_unloading_directive(active_name)

  def init_unloading_directive(self, _name):
    # if new_list is > 160 length, thread the progress else normal progress
    # threading a new progress prevents it from freezing other application activities
    iteration_rate = len(self.unloadingQueue)
    if iteration_rate > 160:
      unListing_thread = Thread(
        target=self.unloadingProgress, name=_name, args=(_name, ))
      unListing_thread.start()
    else:
      self.unloadingProgress(_name)

  def unloadingProgress(self, _name, is_threaded=None):
    iteration_rate = len(self.unloadingQueue)
    if is_threaded is None:
      is_threaded = False if iteration_rate <= 160 else True

    for _ in range(iteration_rate):
      Clock.schedule_once(
        lambda x: self.add_media_to_playlist(_name), 0) \
        if is_threaded else self.add_media_to_playlist(_name)

    Clock.schedule_once(lambda x: self.after_unloading_directive(_name), 1.25)

  def after_unloading_directive(self, list_name):
    if self.unloadingQueue:
      Clock.schedule_once(lambda x: self.after_unloading_directive(list_name), .25)
      return

    # invoke autoplay-protocol to check if the first time auto play is feasible
    self.init_autoplay_protocol(list_name)
    # checking if there still some pending loads to work on
    # if some found, process them in a threaded task
    if self.pendingQueue:
      # getting the next up queue in a line
      nextQueue = self.pendingQueue.pop(0)
      # freeing memory occupied by :attr:`pendingQueue` if no longer viable
      if not self.pendingQueue:
        self.pendingQueue = None
      # accessing nextQueue name to be used as playlist name to assign to
      queue_name = list(nextQueue.keys())[0]
      # charge or load an active queue
      self.unloadingQueue = nextQueue
      # threading unloading process
      threadedUnload = Thread(
        target=self.unloadingProgress, args=(queue_name, True), name=queue_name)
      threadedUnload.start()
    else:
      # perform last task to complete unloading process
      self.unloadingProcess_complete()

  def add_media_to_playlist(self, p_name):
    if not self.unloadingQueue:
      return
    filet = self.unloadingQueue.pop(0)
    playlist = self.does_playlist_exists(p_name)
    media_node = PlayItem(fileSource=filet)
    playlist.ids.play_list.add_widget(media_node)

  def unloadingProcess_complete(self, *largs):
    # clearing memory occupied with pending and unloading queues
    # and resetting them back to initial state
    self.unloadingQueue = self.pendingQueue = None
    # clearing memory occupied by unloadingState and resetting it to initial
    self.unloadingState = None
    # informing the root widget that the process of handling the sent list is done
    # so that the root may cease the activity of progress status
    root = App.get_running_app().root
    root.remove_dropping_status()

  def enable_functionality(self, val):
    self.enablePlaylistDelete = self.enablePlaylistRename = val

  def _create_playlist(self):
    name_input = PlaylistNameInput()
    name_input.children[0].bind(focus=self.check_playlist_name)
    pos_index = len(self.contents.children) - 1
    self.contents.add_widget(name_input, pos_index)

  def _rename_playlist(self):
    # title = self.focused.ids.head_title
    # self.playlistOldTitle = {'parent': title.parent, 'title': title}
    # title.parent.remove_widget(title)
    # _rename = PlaylistNameInput(text=self.focused.title, on_parent=self._attachOldTitle)
    # _rename.children[0].focus = True
    # _rename.children[0].bind(focus=self.check_playlist_new_name)
    # self.focused.add_widget(_rename, 1)
    pass

  def _attachOldTitle(self, *largs):
    # if self.playlistOldTitle and not largs[1]:
    #   parent = self.playlistOldTitle['parent']
    #   title = self.playlistOldTitle['title']
    #   self.playlistOldTitle = None
    #   parent.add_widget(title, 1)
    # super(PlaylistNameInput, largs[0]).on_parent(*largs)
    pass

  def check_playlist_new_name(self, *largs):
    if largs[0].parent.parent and not largs[1]:
      playlist_name = largs[0].text
      if not self.verify_playlist_name(playlist_name):
        largs[0].parent.text = largs[0].text = playlist_name
        self.remove_widget(largs[0].parent)
      else:
        largs[0].text = largs[0].parent.text

  def _delete_playlist(self):
    pass

  def check_playlist_name(self, *largs):
    if largs[0].parent.parent and not largs[1]:
      playlist_name = largs[0].text
      if not self.verify_playlist_name(playlist_name):
        self.contents.remove_widget(largs[0].parent)
        self.init_singlePlaylist(playlist_name)
      else:
        largs[0].text = largs[0].parent.text

  def verify_playlist_name(self, p_name):
    pRegex = re.compile(r'^[a-zA-Z0-9]{2,}(\s[a-zA-Z0-9]+)*$')
    if p_name.lower() == 'enter playlist name' or not pRegex.search(p_name):
      return True
    return bool(self.ids.get(p_name))

  def does_playlist_exists(self, i_name):
    playlist_exist = self.ids.get(i_name)
    if not playlist_exist:
      playlist_exist = self.init_singlePlaylist(i_name)
    return playlist_exist

  def init_singlePlaylist(self, i_name):
    new_playlist = SinglePlaylist(title=i_name, grand_parent=self)
    self.contents.add_widget(new_playlist)
    self.contents.size[1] += 28
    self.ids[i_name] = new_playlist
    return new_playlist

  def init_autoplay_protocol(self, _name):
    root = App.get_running_app().root

    # checking if auto play is feasible
    if not root.ids.play3GUIs.is_ready():
      # getting active playlist name
      if not self.activePlaylist:
        self.activePlaylist = _name

      # accessing a playlist associated to the name pulled
      uniquePlaylist = self.ids[self.activePlaylist]
      # accessing songs list direct parent/container
      songManager = uniquePlaylist.ids.play_list
      # accessing the first song item in line
      firstSongInLine = songManager.children[-1]
      # generating a touch event on the first song item in line
      firstSongInLine.on_down()

  # div - handles playlist and other functions possible
  # when saving, fetching, and updating playlist local file
  def trigger_playlist_save_mode(self, queue, q_name):
    if self.savingQueue is None:
      self.savingQueue = []
    self.savingQueue.append({q_name: (queue, )})

    if self.savingState is None:
      self.savingState = True
      savingProcess = Thread(
        target=self.save_playlist_data, name='playlists save mode', daemon=True)
      savingProcess.start()

  def save_playlist_data(self):
    while 1:
      if not self.savingQueue:
        self.finalize_savingProcess()
        return

      upQueue = self.savingQueue.pop(0)
      queue_name = list(upQueue.keys())[0]
      queue_data = upQueue.get(queue_name)
      upQueue = None
      if len(queue_data) > 1:
        self.apply_playlist_updates(queue_name, queue_data)
      else:
        self.apply_playlist_save(queue_name, queue_data)

  def apply_playlist_updates(self, q_name, q_data):
    pass

  def apply_playlist_save(self, q_name, q_data):
    try:
      json_data = self.open_playlistJSON()
      if json_data:
        playlists = json_data.get('playlists')
        namedPlaylist = playlists.get(q_name)
        if namedPlaylist:
          namedPlaylist.extend(q_data[0])
        else:
          playlists.setdefault(q_name, q_data[0])
    except:
      pass
    finally:
      playlists = namedPlaylist = None
      self.save_JSONData(json_data)

  def finalize_savingProcess(self):
    pass

  def open_playlistJSON(self, mode='r'):
    try:
      with open("./syai3Play/data.json", mode) as json_object:
        json_data = json.load(json_object)
    except Exception as exc:
      Logger.error('SYAI3Play: Cannot data file due to <{}>'.format(exc))
    finally:
      return json_data

  def save_JSONData(self, JSONdata):
    try:
      with open("./syai3Play/data.json", 'w') as json_object:
        json.dump(JSONdata, json_object)
    except Exception as exc:
      Logger.error('SYAI3Play: Cannot save file due to <{}>'.format(exc))


class PlayItemManager(GridLayout):
  focused = ObjectProperty(None, allownone=True)
  ''' contains the selected child
  :attr:`focused` is a :class:`~kivy.properties.ObjectProperty` and
      default to None
  '''

  def on_new_focused(self, child):
    if self.focused is child:
      self.focused = None
    else:
      if self.focused:
        self.focused.admit_focus()
      self.focused = child
      child.change_playing_color()

  def on_focused(self, *largs):
    if not largs[1]:
      return
    root = App.get_running_app().root
    focused_index = self.children.index(largs[1])
    index = len(self.children) - (1 + focused_index)
    root.ids.play3GUIs.autoPlay_backDoor(largs[1].fileSource, index)

  def playback_finished(self, index):
    prop_index = len(self.children) - (1 + index)
    self.children[prop_index].change_playing_color()

  def get_another(self, index, _loop, _random):
    if not self.children:
      return
    # increment index only if _loop allows it
    if _loop != 'one':
      # incrementing current index value so to access associated media
      index += 1
    # in case the index is last in line and there is continuous loop enabled return
    if index == len(self.children):
      if _loop != 'all':
        return
      if _random and len(self.children) > 2:
        self.randomize_media(index)
      else:
        self.children[-1].on_down()
    # in case the index is less than 0, it means user performed previous action
    # when the currently playing media index is 0
    elif index < 0:
      self.children[len(self.children) - 1].on_down()
    # when randomize is enabled
    elif _random and len(self.children) > 2:
      self.randomize_media(index)
    # see the index we have is proportional the mechanism widgets use to order their children,
    # so here I'm going to normalize index to be proportional with widget ordering algorithm
    else:
      propo_index = len(self.children) - (1 + index)
      child = self.children[propo_index]
      if child.selected:
        child.on_down()
      child.on_down()

  def randomize_media(self, index):
    from random import randrange
    # shaking the index list to pick one by chance
    random_index = randrange(0, len(self.children))
    # normalize randomized index to be player proportional
    normal_index = len(self.children) - (1 + random_index)
    # in case both current supposedly index and randomized one equal, swap normal and randomized
    if random_index == index:
      self.children[normal_index].on_down()
    else:
      self.children[random_index].on_down()


class PlaylistNameInput(BoxLayer):
  text = StringProperty('Enter Playlist Name')

  def __init__(self, **kwargs):
    super(PlaylistNameInput, self).__init__(**kwargs)
    self.normal = [.2, .2, .2, 1]
    self.radius = [4]
    self.padding = [10, 0]
    self.size_hint_y = None
    self.height = 28
    name_input = InputField(text=self.text)
    self.add_widget(name_input)

  def on_touch_down(self, touch):
    if not self.collide_point(*touch.pos):
      if self.parent:
        self.parent.remove_widget(self)
    return super(PlaylistNameInput, self).on_touch_down(touch)

  def on_parent(self, *largs):
    root = App.get_running_app().root

    if largs[1]:
      root.ids.play3GUIs.on_leave(Window)
      root.remove_window_cursor_listeners()
    else:
      root.add_window_cursor_listeners()
      root.ids.play3GUIs.on_enter(Window)


class StreamsManager(NavElement):
  focused = None
  source = './Icons/streams.png'

  def alter_focus(self, focus):
    if self.focused:
      if self.focused is focus:
        self.focused = None
        return
      self.focused.alter_selection()
    self.focused = focus


class DownloadManager(NavElement):
  focused = None
  source = './Icons/downloads.png'

  def alter_focus(self, focus):
    if self.focused:
      if self.focused is focus:
        self.focused = None
        return
      self.focused.alter_selection()
    self.focused = focus


class FavoriteManager(NavElement):
  focused = None
  source = './Icons/favorites.png'

  def alter_focus(self, focus):
    if self.focused:
      if self.focused is focus:
        self.focused = None
        return
      self.focused.alter_selection()
    self.focused = focus


class LoadingStatus(BoxLayout):
  message = StringProperty('Loading')
  '''Message to clarify what the loading status is about
  :attr:`message` is a :class:`~kivy.properties.StringProperty` and default to 'Loading'
  '''


class InputField(TextInput):
  write_tab = BooleanProperty(False)
  font_size = NumericProperty('11sp')
  multiline = BooleanProperty(False)
  cursor_color = ListProperty([1, 1, .7, 1])
  background_color = ListProperty([0, 0, 0, 0])
  foreground_color = ListProperty([.8, .5, .5, 1])
  font_name = StringProperty("RobotoMono-Regular")


class HeadBar(GridLayer):
  currentPlaylist = StringProperty('current playlist name')
  ''' the name of the active or current working on playlist
  '''
  viewMode = OptionProperty('mini', options=['mini', 'dock', 'full'])
  '''Used to set a proper view mode with relation its correspondent size

    :attr: is a :class:`kivy.properties` and default to `mini`
    ..Warning:: Only accepts of the its options values
  '''
  strippedViews = None
  '''Temporal container for the stripped views to be reused when needed

    :attr: is a :class:`<dict>` and default to None
  '''

  def __init__(self, **kwargs):
    self.register_event_type('on_drag_window')
    super(HeadBar, self).__init__(**kwargs)

  def getProperty(self, prop_name):
    return getProperty(prop_name)

  def on_touch_down(self, touch):
    if not (not (self.children[0].collide_point(
        *touch.pos) or self.children[1].children[0].collide_point(
      *touch.pos)) and self.collide_point(*touch.pos)):
      return super(HeadBar, self).on_touch_down(touch)

    touch.grab(self)
    Window.grab_mouse()
    pos = pyauto.position()
    left, top = Window.left, Window.top
    self.drag_pos = [pos[0] - left, pos[1] - top]
    return True

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self.dispatch('on_drag_window')

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      touch.ungrab(self)
      Window.ungrab_mouse()

  def on_drag_window(self):
    pos = pyauto.position()
    Window.left, Window.top = (
      pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])

  def do_minimize(self):
    Window.minimize()

  def do_resize(self):
    root = App.get_running_app().root

    if self.viewMode == 'full':
      # preventing window from making auto view switching on resize
      root.resizeLock = True

      x, total_x = root.width, pyauto.size()
      ratio = x / total_x[0]
      if ratio >= .95:
        size = (650, total_x[1] * .5)
      else:
        size = total_x
      Window.size = size

      # updating LeftNavMenu if when resizeLock is enabled
      root.update_left_nav_size(size[0])
      # re-enabling window to make auto view switching on resize
      root.resizeLock = None
    else:
      self.switch_to_full_view()

  def do_terminate(self):
    #  An event for terminating the whole application processes pool
    App.stop(App.get_running_app())

  ''' A division of handling application possible views and Window resize
        auto actions and switching mechanisms
  '''
  def _revealMoreOptions(self):
    root = App.get_running_app().root
    current_s = root.ids.disp_manager.current_screen
    current_s.add_widget(MoreOptions(root=self))

  def on_miniDockSwitch(self, mode):
    if self.viewMode == mode:
      return

    root = App.get_running_app().root
    root.resizeLock = True

    if mode == 'mini':
      self.switch_to_minimal_view()
    else:
      self.switch_to_dock_view()

  def prep_stripped_container(self):
    if self.strippedViews is None:
      self.strippedViews = {}

  def switch_to_minimal_view(self):
    root = App.get_running_app().root

    if self.viewMode == 'full':
      # stripping left-nav from its parent
      left_nav = root.ids.msc_cont.children[1]
      left_nav.parent.remove_widget(left_nav)
      # storing left-nav for later re-use
      self.strippedViews['left-nav'] = left_nav
      # Resizing Window after stripping
      self.resize_window(450, 128)
    else:
      # accessing player GUIs container
      play_gui = root.ids.play3GUIs
      # retrieving row_2 view from store
      row_2 = self.strippedViews['row_2']['self']
      # stripping progress container from its current parent and re-assign it
      progress_cont = play_gui.ids.row_1.children[0]
      progress_cont.parent.remove_widget(progress_cont)
      row_2.children[1].add_widget(progress_cont, 1)
      # restoring row_2 to its original position and parent
      row2_parent = self.strippedViews['row_2']['parent']
      row2_parent.add_widget(row_2)
      # deleting row_2 contents from store
      del self.strippedViews['row_2']
      # Resizing Window after stripping
      Window.size = (450, 128)
      # resetting root resizeLock value to automatic
      root.resizeLock = None
    # resetting view mode to minimal view mode
    self.viewMode = 'mini'

  def switch_to_dock_view(self):
    root = App.get_running_app().root

    if self.viewMode == 'full':
      # stripping left-nav from its parent
      left_nav = root.ids.msc_cont.children[1]
      left_nav.parent.remove_widget(left_nav)
      # storing left-nav for later re-use
      self.strippedViews['left-nav'] = left_nav

    # ensure strippedViews store won't be NoneType
    self.prep_stripped_container()
    # accessing player GUIs container
    play_gui = root.ids.play3GUIs
    # stripping row_2 view from its parent
    row_2 = play_gui.ids.row_2
    row2_parent = row_2.parent
    row2_parent.remove_widget(row_2)
    # stripping progress container view from its parent
    progress_cont = row_2.children[1].children[1]
    progress_cont.parent.remove_widget(progress_cont)
    # storing stripped row_2 view
    self.strippedViews['row_2'] = {'self': row_2, 'parent': row2_parent}
    # volume container shrinking and misplacing
    play_gui.ids.vol_cont.maximum_width = 90
    # adding progress container to row_1
    play_gui.ids.row_1.add_widget(progress_cont)

    # Resizing Window after stripping
    if self.viewMode == 'full':
      self.resize_window(450, 68)
    else:
      Window.size = (450, 68)
      # resetting root resizeLock to automatic react on resize
      root.resizeLock = None

    # resetting view mode to dock mode
    self.viewMode = 'dock'

  def switch_to_full_view(self):
    root = App.get_running_app().root
    root.resizeLock = True

    if self.viewMode == 'dock':
      # switching to minimal view mode first if required
      self.switch_to_minimal_view()
      # after calling the above method this lock is reset to auto so change to manual is needed
      root.resizeLock = True

    # ensure strippedViews store won't be NoneType
    self.prep_stripped_container()
    # retrieving left-nav if store earlier
    left_nav = self.strippedViews.get('left-nav')
    # checking if the left-nav was once already created
    if not left_nav:
      # creating the left-nav for the first time if necessary
      left_nav = LeftNavMenu()
    else:
      # deleting the left-nav if found in store
      del self.strippedViews['left-nav']
    # assigning left-nav to a parent
    root.ids.msc_cont.add_widget(left_nav, 1)
    # resizing window to the minimal size of full mode view
    self.resize_window(650, 250, .14)
    # setting view mode indicator to full mode
    self.viewMode = 'full'

  def resize_window(self, x, y, d=.2):
    animation = Animation(size=(x, y), d=d)
    animation.bind(on_complete=self.resize_animation_complete)
    animation.start(Window)

  def resize_animation_complete(self, *largs):
    root = App.get_running_app().root

    if Window.size[0] == 650:
      root.ids.msc_cont.children[1].width = root.size[0] - 450
    # re-enabling auto mode view switching on window resize
    root.resizeLock = None

  def ensure_existenceOf_leftNav(self):
    '''
    It's to be used when adding dropped files to the playlist widget
        located on the LeftNavMenu widget
    :return:`left-nav` is a :class:`~kivy.property.ObjectProperty` and contains LeftNavMenu
    '''
    root = App.get_running_app().root

    if self.viewMode != 'full':
      # ensure strippedViews is not NoneType
      self.prep_stripped_container()
      left_nav = self.strippedViews.get('left-nav')
      if not left_nav:
        # creating the left-nav for the first time if necessary
        left_nav = LeftNavMenu()
        # storing it
        self.strippedViews['left-nav'] = left_nav
    else:
      # accessing left-nav from root children
      left_nav = root.ids.msc_cont.children[1]

    return left_nav.ids.playlists


class HrzProgressBar(HoverableLabel):
  radius = ListProperty([0])
  normal = ListProperty([.2, .2, .2, .3])
  level_normal = ListProperty([.8, .1, 0, .2])
  handler_normal = ListProperty([.2, .2, .2, 1])
  handler_image = StringProperty('./Icons/yellow.png')

  progressLevel = NumericProperty(0.)
  '''Track bar level in percentage 0.0%
    :attr: is a :class:`~kivy.properties.NumericProperty` and default
      to 0.0
    ..Warnings:: it takes only decimal or real number not percentile
  '''
  stoppedAtLevel = NumericProperty(0.)
  '''Track bar final level in percentage 0.0% after all motion events
    :attr: is a :class:`~kivy.properties.NumericProperty` and default
      to 0.0
    ..Warnings:: it takes only decimal or real number not percentile
  '''
  visible = OptionProperty('none', options=['none', 'off', 'in', 'out'])
  '''Adjuster or handler clocking capability
    :attr: is a :class:`~kivy.properties.OptionProperty` and default
      to None

    ..Warning:: it takes only one among ['off', 'in', 'out', 'none']

    :value::`off`: means the handler is invisible
    :value::`in or out`: means the handler can switch between visible and invisible modes

  '''
  bar_active = BooleanProperty(True)
  '''Disables & Enables the interactivity of the handler

    :attr: is a :class:`~kivy.properties.Boolean` and default to True
    :False::`disables`
    :True::`Enables`
  '''
  autoSwitchMode = None
  '''Automates the visibility mode switching when :attr::visible::`is enabled`
    :attr: is a :object:`~python const` and default to None
  '''
  widthConst = None
  '''previous width container and to be used when auto resize triggered
      in order to re-normalize progressLevel
    :attr: is a :object:`~python const` and default to None
  '''

  def on_size(self, *largs):
    if not self.progressLevel:
      self.widthConst = largs[1][0]
      return
    self.re_normalize_level()

  def on_bar_active(self, *largs):
    if largs[1]:
      self.reveal_handle()
      self.visible = 'in'
    else:
      self.visible = 'off'

    self.disabled = largs[1]

  def on_enter(self):
    if self.visible in ('off', 'none'):
      return
    self.autoSwitchMode.cancel()
    self._changeVisibility()

  def _changeVisibility(self, *largs):
    self.visible = "out" if largs else "in"

  def on_leave(self):
    if self.visible in ('off', 'none'):
      return
    self.autoSwitchMode()

  def on_visible(self, *largs):
    if largs[1] == "out":
      self.hide_handle()
    elif largs[1] == "in":
      if self.autoSwitchMode is None:
        self.autoSwitchMode = Clock.schedule_once(self._changeVisibility, 5)
      else:
        self.reveal_handle()
    elif largs[1] == 'off':
      if self.autoSwitchMode:
        self.autoSwitchMode.cancel()
        self.autoSwitchMode = None
      self.hide_handle()

  def hide_handle(self):
    self.handler_normal[-1] = 0

  def reveal_handle(self):
    self.handler_normal[-1] = 1

  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      if self.bar_active:
        touch.grab(self)
        self._normalize_move_(touch.pos[0])
      return True
    return super(HrzProgressBar, self).on_touch_down(touch)

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self._normalize_move_(touch.pos[0])
    return True

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      self._finalPointLevel(touch.pos[0])
      touch.ungrab(self)
    return True

  def _normalize_move_(self, pos_x):
    self.progressLevel = self.compute_pos_val(pos_x)

  def _finalPointLevel(self, pos_x):
    self.stoppedAtLevel = self.compute_pos_val(pos_x)

  def compute_pos_val(self, pos_x):
    x = pos_x - self.x
    if x < 0:
      x = 0
    elif x > self.size[0]:
      x = self.size[0]
    return x

  def re_normalize_level(self):
    self.progressLevel *= self.size[0] / self.widthConst
    self.widthConst = self.size[0]


class VolumeBar(HrzProgressBar):

  def on_parent(self, *largs):
    if largs[1]:
      Clock.schedule_once(self.initial_player_volume, 1)

  def initial_player_volume(self, *largs):
    if self.size[0] < 101:
      Clock.schedule_once(self.initial_player_volume, .02)
    else:
      vol = SETTINGS.getfloat('MEDIA', 'volume')
      self.progressLevel = self.size[0] * vol


class AutoRollLabel(ScrollInactiveBar):
  text = StringProperty('')
  color = ListProperty([.2, .2, .2, 1])
  font_size = StringProperty('11sp')

  autoScroll = BooleanProperty(False)
  '''Indicates whether the property of scrolling is automated or hovered
     :attr: is a :class:`kivy.properties.Boolean` and default to False
     ..Info::`if False it only scrolls on hover else scheduled for every some seconds
  '''
  scrollHandler = None
  '''Object reserved for auto-scrolling re-schedule when is active as to re-initiate auto-scrolling
     every some seconds after the previous scrolling round

     :attr:`python variable` default to None
  '''
  auto_jump_start = None
  ''' invoked when auto-scroll is enabled to jump start before beginning
          to apply restart_time time-frame rule
  '''
  prevent_many_jumps = None
  ''' Once the auto jump start's attempted, this :attr:`prevent_many_jumps` ensures that there
          will be no more jump start instead :attr:`restart_time` is utilized
  '''
  restart_time = NumericProperty(30)

  def __init__(self, **kwargs):
    super(AutoRollLabel, self).__init__(**kwargs)
    self.animation_1 = None
    self.animation_2 = None

  def on_size(self, *largs):
    root = App.get_running_app().root
    if root.ready is not True:
      return
    self.re_order_schedules()

  def on_children(self, *largs):
    if largs[1]:
      largs[1][0].bind(texture_size=self.on_texture_size)

  def check_viewport_size(self, *largs):
    if not self.size[0]:
      return

    child = self.children[0]
    if child.size[0] > self.size[0]:
      time_frame_const = 35 / 800  # Personal const based on self experience,calculation,observation..
      initial_time = (self.size[0] * time_frame_const)
      duration = (child.size[0] * initial_time / self.size[0])

      if child.hovered and not self.autoScroll:
        self.ready_scroll(child.x, initial_time, duration)
      elif self.autoScroll:
        start_at = 8 if not self.prevent_many_jumps else self.restart_time
        self.auto_jump_start = Clock.schedule_once(
          lambda x: self.ready_scroll(child.x, initial_time, duration), start_at)

  def ready_scroll(self, *largs):
    if self.auto_jump_start:
      self.auto_jump_start = None
      self.prevent_many_jumps = True

    self.animation_1 = Animation(right=largs[0], d=largs[2])
    self.animation_2 = Animation(x=0, d=largs[1])

    self.animation_1.bind(on_complete=self.animation1_complete)
    self.animation_2.bind(on_complete=self.animation2_complete)
    self.animation_1.start(self.children[0])

  def _restart_scroll(self, *largs):
    if self.animation_1:
      self.animation_1.start(self.children[0])

  def on_texture_size(self, *largs):
    largs[0].width = largs[1][0]
    self.prevent_many_jumps = None
    self.re_order_schedules()

  def re_order_schedules(self):
    self.cancel_schedules()
    self.cancel_animations()

    if self.autoScroll:
      self.check_viewport_size()

  def cancel_schedules(self):
    if self.auto_jump_start:
      self.auto_jump_start.cancel()
      self.auto_jump_start = None

    if self.scrollHandler:
      self.scrollHandler.cancel()
      self.scrollHandler = None

  def cancel_animations(self):
    child = self.children[0]
    if self.animation_1:
      self.animation_1.cancel(child)
    if self.animation_2:
      self.animation_2.cancel(child)

    self.reset_viewport()

  def animation1_complete(self, *largs):
    largs[1].x = self.size[0]
    self.animation_2.start(largs[1])

  def animation2_complete(self, *largs):
    if self.autoScroll:
      self.scrollHandler = Clock.schedule_once(
        self._restart_scroll, self.restart_time)

  def compute_restartTime(self, t_frame=None):
    if t_frame is None:
      self.restart_time = 30
    else:
      ratio = int(t_frame / 50)
      if ratio < 3:
        if t_frame > 30:
          self.restart_time = t_frame
        return
      if ratio > 10:
        ratio = int(t_frame / (50 * 9))
      self.restart_time = t_frame / ratio

  def on_enter(self):
    if not self.autoScroll:
      self.check_viewport_size()

  def on_leave(self):
    if not self.autoScroll:
      self.cancel_animations()

  def reset_viewport(self):
    self.children[0].x = 0


class CommonLabelButton(MyButton, HoverableLabel):
  hoverClr = ListProperty([1, .8, 1, .1])


class CustomButton(CommonLabelButton):
  spared = NumericProperty(4)
  h_normal = ListProperty([0, 0, 0, 0])
  normal = ListProperty([1, 1, 1, 1])
  radius = ListProperty([2])
  source = StringProperty("")

  def on_enter(self):
    self.exchange_color()

  def on_leave(self):
    self.exchange_color()

  def exchange_color(self):
    if not self.hoverClr:
      return

    n, h = self.h_normal.copy(), self.hoverClr.copy()
    self.h_normal, self.hoverClr = h, n


class WindowCtrls(CommonLabelButton):
  normal = ListProperty([1, 1, 1, .5])
  source = StringProperty('')

  def on_enter(self):
    self.normal[-1] = 1

  def on_leave(self):
    self.normal[-1] = .5


class MoreOptions(BoxLayer):
  root = ObjectProperty(None, allownone=True)
  '''A reference to root widget and reserved for generating mode switching
       between minimal and dock view events
    :attr: is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''

  def on_touch_down(self, touch):
    if not self.collide_point(*touch.pos):
      if self.parent:
        self.parent.remove_widget(self)
        self.root = None
    return super(MoreOptions, self).on_touch_down(touch)


class PlayItem(CommonLabelButton):
  fileSource = StringProperty('')
  source = StringProperty('./Icons/thumbnail.png')
  selected_normal = ListProperty([1, .3, 0, .1])
  normal = ListProperty([0, 0, 0, 0])
  hoverClr = ListProperty([0, 1, 0, .1])
  selected = BooleanProperty(False)

  def __init__(self, **kwargs):
    super(PlayItem, self).__init__(**kwargs)
    self.text = path.basename(self.fileSource)

  def on_down(self):
    if self.hovered and not self.selected:
      self.on_leave()
    self.selected = not self.selected
    self.parent.on_new_focused(self)

  def admit_focus(self):
    self.selected = not self.selected
    if self.hovered:
      self.on_enter()

  def on_enter(self):
    self.exchange_color()

  def on_leave(self):
    self.exchange_color()

  def exchange_color(self):
    if self.selected:
      return
    n, h = self.normal.copy(), self.hoverClr.copy()
    self.normal, self.hoverClr = h, n

  def change_playing_color(self):
    self.color = [.8, .2, 0, 1] if self.color == [.35, .35, .3, 1] else [.35, .35, .3, 1]


class MainRoot(BoxLayer):
  ready = None
  '''
  Represents the readiness of the main GUIs on start-up
  '''
  resizeLock = True
  '''
  Temporal permission lock when switching modes and changing window size
      `It prevents window auto reshaping on resize while switching mode manually

  :attr: is a :class:`<bool>` and default to None
  '''
  temp_pos = None
  '''
  Temporal position when changing window size manually
  :attr: is a :class:`<list>` and default to None
  '''
  temp_dropped = None
  '''
  Temporal container for all being dropped files
  :att:`temp_dropped` is a :class:`~<list>` and default to None
  '''
  dropping = None
  '''
  Automatic counter measure and activation while the dropping is in progress
  '''

  def __init__(self, **kwargs):
    super(MainRoot, self).__init__(**kwargs)
    self.ready = Clock.schedule_interval(self._getReady_, .1)

  @staticmethod
  def getProperty(prop_name):
    return getProperty(prop_name)

  def on_size(self, *largs):
    if self.resizeLock is None:
      self.update_left_nav_size(largs[1][0])

  def update_left_nav_size(self, width):
    # enforcing LeftNavMenu size restriction on window resize
    if len(self.ids.msc_cont.children) > 1:
      left_nav = self.ids.msc_cont.children[1]
      left_nav.max_size = width - 450

  def playlist_fromCLI(self, *largs):
    print(largs)  # Capture all inputs from command line on startup

  def _getReady_(self, *largs):
    if self.ids:
      # cancelling the auto checkup and confirming readiness
      self.ready.cancel()
      self.ready = True
      # positioning window on startup
      startUp_window_pos()
      # turning volume and media progress bars interacting
      self.ids.play3GUIs.add_progressBars_listeners()
      # listening to mouse position relative to window so to set custom keypad
      self.add_window_cursor_listeners()
      # enabling auto view mode switch on window resize
      self.resizeLock = None
      self.enable_dropFile()

  def add_window_cursor_listeners(self):
    play3 = self.ids.play3GUIs
    Window.bind(on_cursor_enter=play3.on_enter, on_cursor_leave=play3.on_leave)

  def remove_window_cursor_listeners(self):
    play3 = self.ids.play3GUIs
    Window.unbind(on_cursor_enter=play3.on_enter, on_cursor_leave=play3.on_leave)

  def enable_dropFile(self):
    Window.bind(on_dropfile=self.on_file_dropped)

  def on_file_dropped(self, *largs):
    if self.dropping is None:
      # mapping a dropping status widget
      self.show_dropping_status()
      # creating after dropping counter measure
      self.dropping = Clock.schedule_once(self.after_all_dropped, 1.4)
    # freezing after dropping counter measure just to sort a dropped file
    self.dropping.cancel()
    # decoding dropped file to <class str>
    dropped_file = largs[1].decode('utf-8')
    self.verify_file_address(dropped_file)
    # unfreeze after dropping counter measure
    self.dropping()

  def after_all_dropped(self, *largs):
    # clearing the auto measure after dropping for a fresh start
    self.dropping = None

    # ensure that :attr:`temp_dropped` is an empty list
    if not self.temp_dropped:
      self.temp_dropped = None
      self.remove_dropping_status()
      return

    # swapping temp_dropped to another container so that it can be wiped clean
    copyOf_dropped = self.temp_dropped
    # wiping clean temp_dropped container for a fresh start
    self.temp_dropped = None
    # retrieving playlists container
    playlists_manager = self.ensure_existenceOf_leftNav()
    # making some decision on a new coming list content of where to put them
    playlists_manager._decisionOn_newList(copyOf_dropped)

  def verify_file_address(self, address):
    if not path.exists(address):
      return

    # the address points to a folder
    if path.isdir(address):
      # listing its contents
      contents = listdir(address)
      # checking if contents exist, if so, add the address to the temp_dropped
      if contents:
        self.initiate_temp_dropped()
        self.temp_dropped.append(address)
      else:
        return

    # the address points to file
    elif path.isfile(address):
      # reading accepted file formats from settings file
      formats = json.loads(SETTINGS.get('MEDIA', 'formats'))
      # getting the file format
      format_index = address.rsplit('.', 1)[-1]
      # checking if the file format is compatible with accepted ones
      # if so, add the address to the temp_dropped
      if format_index.lower() in formats:
        self.initiate_temp_dropped()
        self.temp_dropped.append(address)
      else:
        return

  def disable_dropFile(self):
    # disabling file dropping capability
    Window.unbind(on_dropfile=self.on_file_dropped)

  def show_dropping_status(self):
    loading = LoadingStatus(
      padding=(0, 5), size_hint_x=None, width=55)
    self.ids.head_bar.ids.posterOffice.add_widget(loading, 2)

  def remove_dropping_status(self):
    poster = self.ids.head_bar.ids.posterOffice
    poster.remove_widget(poster.children[2])

  def initiate_temp_dropped(self):
    '''
    invoked when trying to initiate :attr:`temp_dropped` for the first use
    :return:
    '''

    if self.temp_dropped is None:
      self.temp_dropped = []

  def ensure_existenceOf_leftNav(self):
    '''
    It's to be used when adding dropped files to the playlist widget
        located on the LeftNavMenu widget
    :return:`left-nav` is a :class:`~kivy.property.ObjectProperty` and contains LeftNavMenu
    '''
    return self.ids.head_bar.ensure_existenceOf_leftNav()


class PlayScreen(Screen):
  # app main screen
  pass


class Play3(BoxLayout):
  __soundPlayer = ObjectProperty(None, allownone=True)
  ''' Audio sound loader or provider or engine
  :attr:`__soundPlayer` is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''
  threadForCurrent = None
  ''' A continuous running clock that reads current position from the playing media
  :attr:`threadForCurrent` is a :class:`~<built-in 'object'>` and default to None
  '''
  source = StringProperty('')
  ''' File address to load in from the local storage as media data to play
  :attr:`source` is a :class:`~kivy.properties.StringProperty` and default to ''
  '''
  volume = NumericProperty(0.)
  ''' Sound level for the media player either playing or not
        this values between 0 and 1 never beyond the scope
  :attr:`volume` is a :class:`~kivy.properties.NumericProperty` and default to 0.
  '''
  seek_pos = NumericProperty(None, allownone=True)
  ''' Position value to jump to while the media is in play or pause state
        the value is always between 0. and the estimated time-frame of the media
  :attr:`seek_pos` is a :class:`~kivy.properties.NumericProperty` and default to None
  '''
  duration = NumericProperty(None, allownone=True)
  ''' Estimated time-frame the media is supposedly to last if not otherwise
  :attr:`duration` is a :class:`~kivy.properties.NumericProperty` and default to None
  '''
  current_pos = NumericProperty(None, allownone=True)
  ''' Estimated time-frame the media is supposedly to last if not otherwise
  :attr:`duration` is a :class:`~kivy.properties.NumericProperty` and default to None
  '''
  state = OptionProperty('stop', options=['stop', 'play', 'pause'])
  ''' Media playing status
  :attr:`state` is a :class:`~kivy.properties.OptionProperty` and default to 'stop'
  ..Warning::attr~state: accepts only one of 'stop', 'play', 'pause'
  '''
  _loop = OptionProperty('none', options=['none', 'one', 'all'])
  '''
  '''
  _shuffle = BooleanProperty(False)
  '''
  '''
  force_stop = BooleanProperty(False)
  '''
  '''
  nextIndex = NumericProperty(None, allownone=True)
  '''
  '''
  currentIndex = NumericProperty(None, allownone=True)
  '''
  '''
  prevent_play_another = None

  # when cursor enters window canvas, request custom keyboard
  def on_enter(self, window):
    self._keyboard = None
    self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
    self._keyboard.bind(on_key_down=self._on_key_down)

  # when cursor leaves window canvas, release custom keyboard
  def on_leave(self, window):
    try:
      self._keyboard.unbind(on_key_down=self._on_key_down)
      self._keyboard = None
    except Exception:
      pass

  # handle key presses
  def _on_key_down(self, keypad, code, char, mod):
    if char == 's':
      self.stop_playback()
    elif char == 'n':
      self._next()
    elif char == 'p':
      self._previous()
    elif char == 'l':
      self._loop_alter(self.ids.loope)
    elif char == 'm':
      self.volume_hypothesis('mute')
    elif char == 'r':
      self._shuffle_alter(self.ids.shufflee)
    elif char == 'e':
      self.headBar_hypothesis('mini')
    elif char == 'd':
      self.headBar_hypothesis('dock')
    elif char == 'f':
      self.headBar_hypothesis('full')
    elif char == 'q':
      self.headBar_hypothesis('quit')
    elif code[1] == 'spacebar':
      self.play_pause(self.ids.pp)
    elif code[1] == 'up' and 'ctrl' in mod:
      self.volume_hypothesis('up')
    elif code[1] == 'down' and 'ctrl' in mod:
      self.volume_hypothesis('down')
    elif code[1] == 'left' and 'shift' in mod:
      self.backward_wind()
    elif code[1] == 'right' and 'shift' in mod:
      self.forward_wind()

  # keyboard hypothesis
  def volume_hypothesis(self, course):
    tuner = self.ids.volTuner
    if course == 'up':
      vol = tuner.progressLevel + (tuner.size[0] * .05)
    elif course == 'down':
      vol = tuner.progressLevel - (tuner.size[0] * .05)
    elif course == 'mute':
      vol = 10e-24

    if vol < 0:
      vol = 10e-24
    elif vol > tuner.size[0]:
      vol = tuner.size[0]
    tuner.progressLevel = vol

  def headBar_hypothesis(self, course):
    headBar = App.get_running_app().root.ids.head_bar
    if course == 'full':
      headBar.do_resize()
    elif course == 'mini':
      headBar.on_miniDockSwitch('mini')
    elif course == 'dock':
      headBar.on_miniDockSwitch('dock')
    elif course == 'quit':
      headBar.do_terminate()

  # after the cursor leaves the window canvas end the keypad is released, do this
  def _keyboard_closed(self):
    pass

  # back door used to check if auto play is feasible
  def is_ready(self, cpl=None):
    return bool(self.__soundPlayer) if not cpl else self.state == 'stop'

  # back door to initiate sneaking playing or auto play
  def autoPlay_backDoor(self, source, index):
    # ensures that if there is a playback stops first
    if self.source:
      self.prevent_play_another = True
      self.apply_stop()
    # assign current media source index from its container
    self.currentIndex = self.nextIndex = index
    # media source address to load its data
    self.source = source

  # div - Receiving a new media file source
  def on_source(self, *largs):
    # ensure NoneType or empty is not accepted
    if not largs[1]:
      return

    if self.__soundPlayer is None:
      self.init_player(largs[1])
    else:
      self.apply_stop()
      self.__soundPlayer.source = largs[1]
    self.apply_play()

  # div - receiving volume new level and applying it
  def on_volume(self, *largs):
    if self.__soundPlayer is None:
      return
    self.__soundPlayer.volume = largs[1]

  # div - handling new changes in media status instantly
  def on_state(self, *largs):
    pass

  # div - jump to the new received position value
  def on_seek_pos(self, *largs):
    # ensure NoneType is not accepted
    if largs[1] is None:
      return
    # now seeking new position value
    if self.state == 'pause':
      self.current_pos = largs[1]
    elif self.state == 'play':
      self.threadForCurrent.cancel()
      self.__soundPlayer.seek(largs[1])
      self.threadForCurrent()

    # resetting :attr:`seek_pos` to its initial value None
    self.seek_pos = None

  # div - GUI value update with the estimated and elapsed time-frame of the playing media
  def on_duration(self, *largs):
    # ensure NoneType is not accepted
    if largs[1] is None:
      return
    # updating GUI to match current duration value
    self.ids.time_estimate.time_stamp = largs[1]
    self.ids.track_name.compute_restartTime(largs[1])

  def on_current_pos(self, *largs):
    # ensure NoneType is not accepted
    if largs[1] is None:
      return
    # updating GUI to match current pos value
    self.ids.time_lap.time_stamp = largs[1]
    self.ids.mediaPos.progressLevel = (
        (largs[1] / self.duration) * self.ids.mediaPos.size[0])

  # div - player initiation for the first time
  def init_player(self, filet):
    self.__soundPlayer = SoundLoader.load(filet)
    self.__soundPlayer.volume = self.volume
    self.add_listeners()

  # div - retrieving playing media duration time-frame
  ## And initiate the current_pos getter thread
  def get_length(self, *largs):
    length = self.get_media_duration()

    if (length <= 0) or (type(length) is not float):
      Clock.schedule_once(self.get_length, .02)
    else:
      self.duration = length
      if self.threadForCurrent is None:
        self.threadForCurrent = Clock.schedule_interval(self.get_pos, .01)
      else:
        self.threadForCurrent()

  # mechanism to access the media duration even when not playing
  def get_media_duration(self):
    from tinytag import TinyTag
    song_detail = TinyTag.get(self.source)
    return song_detail.duration

  # div - current-pos getter handler
  def get_pos(self, *largs):
    current_pos = self.__soundPlayer.get_pos()
    self.current_pos = 0 if current_pos < 0 else current_pos

  # div - status handler for the media loader itself, in here it decides
  # on whether to continue playing given available options or cease playing
  def on_media_state(self, *largs):
    if largs[1] == 'stop':
      self.threadForCurrent.cancel()

      if self.force_stop:
        self.reset_player_protocol()
      else:
        if self.state == 'play':
          self.reset_player_GUIs()
          if self.prevent_play_another:
            self.prevent_play_another = None
          else:
            self.play_another_protocol()
    else:
      if self.state == 'stop':
        self.get_length()
        self.update_player_GUIs()

  # div - applying stop features while media player is in pause or play state
  # ..this method is invoked only when trying to load another while another's loaded before
  def apply_stop(self):
    if self.state == 'pause':
      self.on_media_state('', 'stop')
    else:
      self.__soundPlayer.stop()

  # div - applying pause features while media player is playing
  def apply_pause(self):
    self.state = 'pause'
    self.__soundPlayer.stop()

  # div - applying resume or replay features
  def apply_play(self):
    self.__soundPlayer.play()

    if self.state == 'pause':
      self._resume_protocol()

  # div - applying resume media protocol
  def resume(self, *largs):
    length = self.__soundPlayer.length
    if (length <= 0) or (type(length) is not float):
      Clock.schedule_once(self.resume, .02)
    else:
      self.__soundPlayer.volume = self.volume
      self.seek_pos = self.current_pos
      self.threadForCurrent()

  def _resume_protocol(self):
    self.__soundPlayer.volume = 0
    self.state = 'play'
    self.resume()
    self.ids.pp.source = './Icons/pause.png'

  # div - after a forced stop protocol
  def reset_player_protocol(self):
    self.force_stop = False
    self.reset_player_GUIs()

  # div - ensures a continuous playback given right options
  def play_another_protocol(self):
    # accessing activePlaylist widget
    uniquePlaylist = self.get_activePlaylist()
    # scheduling another available media
    uniquePlaylist.ids.play_list.get_another(
      index=self.nextIndex, _loop=self._loop, _random=self._shuffle)

  # get an active playlist
  def get_activePlaylist(self):
    root = App.get_running_app().root
    # accessing playlistManager widget
    playlistManager = root.ids.head_bar.ensure_existenceOf_leftNav()
    # accessing activePlaylist widget and returning it
    return playlistManager.ids[playlistManager.activePlaylist]

  # div - media loader event listeners
  def remove_listeners(self):
    self.__soundPlayer.unbind(state=self.on_media_state)

  def add_listeners(self):
    self.__soundPlayer.bind(state=self.on_media_state)

  # div - progress bars event listeners' handlers
  def add_progressBars_listeners(self):
    self.ids.volTuner.bind(progressLevel=self._adjust_volume)
    self.ids.mediaPos.bind(stoppedAtLevel=self._seek_pos)

  def _adjust_volume(self, *largs):
    self.volume = largs[1] / largs[0].size[0]

  def _seek_pos(self, *largs):
    self.seek_pos = largs[1] * self.duration / largs[0].size[0]

  # div - GUIs reset after playing or in case of shifting to another media
  def reset_player_GUIs(self):
    # resetting local variables to initial status
    self.source = ''
    self.state = 'stop'
    self.change_colorOf_mediaItem()
    self.duration = self.seek_pos = self.current_pos = None
    # resetting back to initial status GUI features
    self.ids.pp.source = './Icons/play.png'
    self.ids.track_format.textVal = ' '
    self.ids.mediaPos.progressLevel = 10e-24
    self.ids.mediaPos.bar_active = False
    self.ids.track_name.text = 'No track'
    self.ids.time_lap.time_stamp = None
    self.ids.time_estimate.time_stamp = None
    self.ids.track_name.color = [.2, .2, .2, 1]
    self.ids.track_name.compute_restartTime()

  def change_colorOf_mediaItem(self):
    # accessing the active playlist widget
    uniquePlaylist = self.get_activePlaylist()
    # changing text color of the current track to initial
    uniquePlaylist.ids.play_list.playback_finished(self.currentIndex)

  # div - setting up ready and smart the GUIs when media play-state initiated
  def update_player_GUIs(self):
    self.state = 'play'
    self.ids.pp.source = './Icons/pause.png'

    self.ids.mediaPos.bar_active = True
    self.ids.track_name.color = [.6, 1, .6, 1]
    self.ids.track_name.text = path.basename(self.source)
    self.ids.track_format.textVal = self.source.rsplit('.', 1)[-1].lower()

  # div - manual controls and directives on media with GUI features
  def play_pause(self, *largs):
    if self.__soundPlayer is None:
      return

    if self.state == 'play':
      self.apply_pause()
      largs[0].source = './Icons/play.png'
    elif self.state == 'pause':
      self.apply_play()
    else:
      self.nextIndex -= 1
      self.play_another_protocol()

  def stop_playback(self):
    # ensures that this course of action only applied when playing
    if (self.__soundPlayer is None) or (self.state == 'stop'):
      return

    self.force_stop = True
    self.apply_stop()

  def forward_wind(self):
    # ensures that this course of action only applied when playing
    if (self.__soundPlayer is None) or (self.state == 'stop'):
      return

    # jumping forward 5 secs on the current pos
    jump_pos = self.current_pos + 5.
    # ensuring that the jump is never greater than the media duration
    if jump_pos > self.duration:
      jump_pos = self.duration
    self.seek_pos = jump_pos

  def backward_wind(self):
    # ensures that this course of action only applied when playing
    if (self.__soundPlayer is None) or (self.state == 'stop'):
      return

    # jumping forward 5 secs on the current pos
    jump_pos = self.current_pos - 5
    # ensuring that the jump is never less than media initial pos which is 0.
    if jump_pos < 0.:
      jump_pos = 0.
    self.seek_pos = jump_pos

  def _next(self):
    # ensures that this course of action only applied when playing
    if (self.__soundPlayer is None) or (self.state == 'stop'):
      return
    if self._loop == 'one':
      self.nextIndex += 1
    self.apply_stop()

  def _previous(self):
    # ensures that this course of action only applied when playing
    if (self.__soundPlayer is None) or (self.state == 'stop'):
      return
    if self._loop == 'one':
      self.nextIndex -= 1
    else:
      self.nextIndex -= 2
    self.apply_stop()

  def _loop_alter(self, *largs):
    self._loop, _source = {
      'none': ['one', 'repeat-1.png'], 'one': ['all', 'repeat-all.png'],
      'all': ['none', 'repeat-off.png']}.get(self._loop)
    largs[0].source = path.join('./Icons', _source)

  def _shuffle_alter(self, *largs):
    self._shuffle = not self._shuffle
    largs[0].source = path.join(
      './Icons', 'shuffle-on.png' if self._shuffle else 'shuffle-off.png')


class SplashScreen(BoxLayer):
  def __init__(self, **kwargs):
    super(SplashScreen, self).__init__(**kwargs)
    self.padding = (150, 54)
    self.normal = [.12, .12, .15, 1]
    self.outl_clr = [.4, .3, .3, .4]
    self.outl_w = 2
    self.add_widget(LoadingStatus(message='Please wait..'))
    Clock.schedule_once(self._main_window_ready, 10)

  def _main_window_ready(self, c_frame):
    app = App.get_running_app()
    Window.remove_widget(self)
    root = _mainRoot_ if _mainRoot_ else MainRoot()
    Window.add_widget(root)
    app.root = root


class MainApp(App):
  title = 'SYAI3Play'
  use_kivy_settings = False

  def build(self):
    return SplashScreen() if _mainRoot_ else MainRoot()

  def on_start(self):
    pass

  def on_minimize(self):
    pass

  def on_restore(self):
    pass

  def on_maximize(self):
    pass

  def on_stop(self, *largs):
    try:
      self.config.read(path.join(self.directory, 'settings.ini'))
      self.config["window"]["window"] = json.dumps({
        'window-size': [450, 128],
        'window-pos': [Window.left, Window.top]
      })
      self.config.write()
    except:
      Logger.error("SYAI3Play: CONFIG")

    sys.exit(0)


_mainRoot_ = None

if __name__ == '__main__':
  if len(sys.argv) > 1:
    _mainRoot_ = MainRoot()
    _mainRoot_.playlist_fromCLI(sys.argv[1:])

  MainApp().run()
