# encoding: utf-8

import e32
import appuifw
import topwindow
import graphics

class AppSkel(object):
    _TAB_TITLE = 0
    _TAB_CREATE_BODY = 1
    _TAB_CREATE_MENU = 2
    _TAB_BODY = 3
    _TAB_MENU = 4

    selected_tab = 0

    def __init__(self):
        # initialization
        self.init()

        self._mainlock = e32.Ao_lock()

        # tabs
        self._tabs = []
        if self.tabs():
            appuifw.app.set_tabs(
                self._create_tabs(),
                self._internal_tab_callback)
        else:
            appuifw.app.body = self.body()
            appuifw.app.menu = self._create_menu()

        # menu
        appuifw.app.exit_key_handler = self.quit


        # final setup
        self.setup()

    # Methods to be reimplemented
    def body(self):
        "This method returns the body object of UI."
        raise NotImplemented("Implement this method in subclass.")

    def setup(self):
        "This method will be called to initialize the UI"
        raise NotImplemented("Implement this method in subclass.")

    def confirm_exit(self):
        "This method will be called before exit. Return False to abort exit."
        return True

    def tabs(self):
        """Return a sequence of (title, callback) tuple for tabs or
        an empty sequence for no tabs (default)"""
        return []

    def menu(self):
        """Return a sequence of (title, callback|submenu) tupple for
        menu options."""
        return []
    #/

    def _create_menu(self):
        menu = list(self.menu())
        if hasattr(self, 'menu_help'):
            menu.append( (u'Help', self.menu_help) )
        if hasattr(self, 'menu_about'):
            menu.append( (u'About', self.menu_about) )
        menu.append( (u'Exit', self.quit) )
        return menu

    def _create_tabs(self):
        tabs = self.tabs()
        
        titles = []
        for tab in tabs:
            title = tab[0]
            if len(tab) == 3:
                self._tabs.append( [ title, tab[1], tab[2], None, None ] )
            else:
                self._tabs.append( [ title, tab[1], None, None, None ] )
            titles.append(title)
        return titles

    def _internal_tab_callback(self, index):
        tab = self._tabs[index]
        if tab[AppSkel._TAB_BODY] is None:
            tab[AppSkel._TAB_BODY] = tab[AppSkel._TAB_CREATE_BODY]()
        if tab[AppSkel._TAB_MENU] is None:
            if tab[AppSkel._TAB_CREATE_MENU]:
                tab[AppSkel._TAB_MENU] = tab[AppSkel._TAB_CREATE_MENU]() + self._create_menu()
            else:
                tab[AppSkel._TAB_MENU] = self._create_menu()
        appuifw.app.body = tab[AppSkel._TAB_BODY]
        appuifw.app.menu = tab[AppSkel._TAB_MENU]

    def activate_tab(self, index):
        self._internal_tab_callback(index)
        appuifw.app.activate_tab(index)
        self.selected_tab = index

    def _get_title(self):
        return appuifw.app.title
    def _set_title(self, title):
        appuifw.app.title = title
    title = property(_get_title, _set_title)

    def _center_text(self, d_canvas, y, msg, font='dense'):
        box, pixels, chars = d_canvas.measure_text(msg, font=font)
        txt_size = (box[2] - box[0], box[3] - box[1])
        y += txt_size[1] + 6
        d_canvas.text(((d_canvas.size[0]-txt_size[0])/2,y), msg, font=font)
        return y

    def about_dialog(self, name, version, year, authors, icon, license):
        self._about_lock = e32.Ao_lock()
        self._old_exit = appuifw.app.exit_key_handler
        self._old_menu = appuifw.app.menu

        size, pos = appuifw.app.layout(appuifw.EScreen)

        self._old_orientation = appuifw.app.orientation
        if appuifw.app.orientation != 'portrait': # TODO: implement dialog box for landscape UI
            appuifw.app.orientation = 'portrait'

        appuifw.app.menu = [(u'Close', self._exit_about_dialog), ]
        appuifw.app.exit_key_handler = self._exit_about_dialog

        d_size = (size[0] - 23, size[1] - 100)
        d_pos = (10, (size[1] - d_size[1]) / 2)
        d_canvas = graphics.Image.new(d_size)
        d_canvas.clear(0xFFFFFF)
        y = 6

        icon = graphics.Image.open(icon)
        d_canvas.blit(icon, target=((d_size[0]-icon.size[0])/2,y))
        y += icon.size[1]
        
        y = self._center_text(d_canvas, y, name, 'title')
        y = self._center_text(d_canvas, y, version, 'legend')
        y = self._center_text(d_canvas, y + 6, u"Copyright © " + year, 'dense')
        for author in authors:
            y = self._center_text(d_canvas, y, author, 'dense')
        y = self._center_text(d_canvas, y + 6, license, 'legend')

        self._about_window = topwindow.TopWindow()
        self._about_window.add_image(d_canvas, (0,0))

        self._about_window.position = d_pos
        self._about_window.size = d_size
        self._about_window.shadow = 3
        self._about_window.corner_type = 'square'
        self._about_window.show()

        self._about_lock.wait()

    def _exit_about_dialog(self):
        appuifw.app.menu = self._old_menu
        appuifw.app.exit_key_handler = self._old_exit
        appuifw.app.orientation = self._old_orientation
        self._about_window.hide()
        self._about_lock.signal()

    def run(self):
        self._mainlock.wait()

    def quit(self):
        if not self.confirm_exit():
            return
        appuifw.app.set_tabs([], None)
        self._mainlock.signal()
