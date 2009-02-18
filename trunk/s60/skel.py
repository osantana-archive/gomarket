# encoding: utf-8

import e32
import appuifw

class AppSkel(object):
    TAB_TITLE = 0
    TAB_CREATE = 1
    TAB_BODY = 2
    def __init__(self):
        self._mainlock = e32.Ao_lock()
        
        # tabs
        self._tabs = []
        if self.tabs():
            appuifw.app.set_tabs(
                self._create_tabs(self.tabs()),
                self._internal_tab_callback)
            self._internal_tab_callback(0)
        else:
            appuifw.app.body = self.body()

        # menu
        menu = list(self.menu())
        if hasattr(self, 'menu_help'):
            menu.append( (u'Help', self.menu_help) )
        if hasattr(self, 'menu_about'):
            menu.append( (u'About', self.menu_about) )
        menu.append( (u'Exit', self.quit) )
        appuifw.app.menu = menu
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

    def _create_tabs(self, tabs):
        titles = []
        for title, create_callback in tabs:
            self._tabs.append( [ title, create_callback, None ] )
            titles.append(title)
        return titles
        
    def _internal_tab_callback(self, index):
        tab = self._tabs[index]
        if tab[AppSkel.TAB_BODY] is None:
            tab[AppSkel.TAB_BODY] = tab[AppSkel.TAB_CREATE]()
        appuifw.app.body = tab[AppSkel.TAB_BODY]

    def _get_title(self):
        return appuifw.app.title
    def _set_title(self, title):
        appuifw.app.title = title
    title = property(_get_title, _set_title)

    def run(self):
        self._mainlock.wait()
        
    def quit(self):
        if not self.confirm_exit():
            return
        self._mainlock.signal()