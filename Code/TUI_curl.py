from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, Label
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
import os
import json

# Loading the data into JSON
HELP_TEXT = "Navigate with ARROW KEYS. Select with ENTER. Switch the active section of the interface with TAB"

global_state = ""

class DataModel(object):
    def __init__(self, structure_path):
        # read in data
        with open(structure_path) as sreader:
            self.structure_data = json.load(sreader)

# The three views displaying various levels of flag information


class ListBoxView(Frame):
    def __init__(self, screen, content, next_screen, previous_screen, screen_title, custom_text=None, help_text=None):
        super(ListBoxView, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          on_load=self._reload_list,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title=screen_title)

        # add summary
        if custom_text != None:
            self._label = Label(custom_text)
            layout_label = Layout([100])
            self.add_layout(layout_label)
            layout_label.add_widget(self._label)
            layout_label.add_widget(Divider())

        # add content
        self._list_view = ListBox(Widget.FILL_FRAME,
                                  [("A", 1)],
                                  name="rsync Flags",
                                  add_scroll_bar=True,
                                  on_select=self._on_select
                                  )

        layout_list_view = Layout([100], fill_frame=True)
        self.add_layout(layout_list_view)

        layout_list_view.add_widget(self._list_view)
        layout_list_view.add_widget(Divider())

        # adding buttons
        self._back_button = Button("Back", self._back)
        layout_buttons = Layout([50, 50])
        self.add_layout(layout_buttons)
        layout_buttons.add_widget(self._back_button, 0)

        self._quit_button = Button("Quit", self._quit)
        layout_buttons.add_widget(self._quit_button, 1)

        # disabling back button on main screen
        # if (screen_title=="Flag Categories"):
        # 	self._back_button.disabled = True

        # add help text
        if help_text != None:
            # layout_buttons.add_widget(Divider())
            self._help_label = Label(help_text)
            layout_help_label = Layout([100])
            self.add_layout(layout_help_label)
            layout_help_label.add_widget(Divider())
            layout_help_label.add_widget(self._help_label)

        # fix layout
        self.fix()

        # copy in class variables
        self._next_screen = next_screen
        self._previous_screen = previous_screen
        self._screen_title = screen_title

        self._content = content
        self._categories = []
        self._sub_categories = []
        self._flag_info = []

    def _reload_list(self, new_value=None):
        global global_state

        # categories screen

        if self._screen_title == "Flag Categories":
            self._categories = []
            i = 1
            for key in self._content.structure_data.keys():
                self._categories.append((key, i))
                i = i + 1
            self._list_view.options = self._categories
            self._list_view.value = new_value

        # subcategories
        elif self._screen_title == "Flag SubCategories":
            augmented_key = global_state
            category_key = augmented_key.split(":")[0]
            self._sub_categories = []
            j = 1
            for key in self._content.structure_data[category_key]:
                self._sub_categories.append((key, j))
                j = j + 1
            self._list_view.options = self._sub_categories
            self._list_view.value = new_value

        # flag info
        elif self._screen_title == "Flag Info":
            augmented_key = global_state
            category_key = augmented_key.split(":")[0]
            subcategory_key = augmented_key.split(":")[1]
            self._flag_info = []
            k = 1

            et = self._content.structure_data[category_key]
            rr = et[subcategory_key]

            for val in rr:
                self._flag_info.append(
                    (val["flag"] + " : " + val["short-description"], k))
                k = k + 1
            self._list_view.options = self._flag_info
            self._list_view.value = new_value

        else:
            self._list_view.options = [("A", 1)]
            self._list_view.value = new_value

    def _on_select(self):
        global global_state

        # categories screen
        if self._screen_title == "Flag Categories":
            selected_key = self._categories[self._list_view.value - 1][0]
            global_state = selected_key
            raise NextScene(self._next_screen)

        # subcategories screen
        elif self._screen_title == "Flag SubCategories":
            sub_key = self._sub_categories[self._list_view.value - 1][0]
            category_key = global_state.split(":")[0]
            augmented_key = category_key + ":" + sub_key
            global_state = augmented_key
            raise NextScene(self._next_screen)

        # if self._next_screen==None:
        # 	data = self._content[self._list_view.value - 1][0]
        # 	# global_state = (data)

        # else:
        # 	raise NextScene(self._next_screen)

    def _back(self):
        raise NextScene(self._previous_screen)

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")

# The usage screen


class LandingView(Frame):
    def __init__(self, screen, help_text=None):
        super(LandingView, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          # on_load=self._reload_list,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="curl Help Page")

        # layout_label.add_widget(Divider())

        # layout_buttons.add_widget(Divider())
        self._help_label = Label(help_text)
        layout_help_label = Layout([100])
        self.add_layout(layout_help_label)
        layout_help_label.add_widget(self._help_label)
        layout_help_label.add_widget(Divider())

        # adding buttons
        self._continue_button = Button("Continue", self._continue)
        layout_buttons = Layout([50, 50])
        self.add_layout(layout_buttons)
        layout_buttons.add_widget(self._continue_button, 0)

        self._quit_button = Button("Quit", self._quit)
        layout_buttons.add_widget(self._quit_button, 1)

        # add summary
        custom_text = "curl [options / URLs]\n\nDescription\ncurl is a tool to transfer data from or to a server, using one of the supported protocols (DICT, FILE, FTP, FTPS, GOPHER, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, POP3, POP3S, RTMP, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET and TFTP).\n\nUsage\nThe following example simulates a GET request for a website URL, using a username and password for basic HTTP authentication:\n\ncurl --user name:password http://www.bbb.com"
        self.data = {"usage": custom_text}

        self._label = TextBox(Widget.FILL_FRAME, "Usage",
                              "usage", as_string=True, line_wrap=True)
        self._label.custom_colour = "selected_field"

        self._label.disabled = True
        layout_label = Layout([100])
        self.add_layout(layout_label)
        layout_label.add_widget(Divider())
        layout_label.add_widget(self._label)

        # fix layout
        self.fix()

    def _continue(self):
        raise NextScene("Flag Categories")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


def demo(screen, scene):
    scenes = [Scene(
        [LandingView(screen=screen, help_text="Navigate with ARROW KEYS and TAB")],
        -1,
        name="Landing"),
        Scene(
        [ListBoxView(screen=screen, content=model, next_screen="Flag SubCategories", previous_screen="Landing", screen_title="Flag Categories",
                     help_text=HELP_TEXT)],
        -1,
        name="Flag Categories"),
        Scene(
        [ListBoxView(screen=screen, content=model, next_screen="Flag Info", previous_screen="Flag Categories",
                     screen_title="Flag SubCategories", help_text=HELP_TEXT)],
        -1,
        name="Flag SubCategories"),
        Scene(
        [ListBoxView(screen=screen, content=model, next_screen=None, previous_screen="Flag SubCategories",
                     screen_title="Flag Info", help_text=HELP_TEXT)],
        -1,
        name="Flag Info")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


# class FlagInfoView(Frame):
# 	def __init__(self, screen, content):


last_scene = None

structure_path = "../documentation/curl_doc/doc.json"
model = DataModel(structure_path)
selected_value = "Establish a Transfer:Requests and Responses"
global_state = selected_value

while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
