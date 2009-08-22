import os, sys
import random

import wx

import garlicsim
import guiproject
import misc.notebookctrl as notebookctrl
import customwidgets

import misc.threadtimer as threadtimer

#import psyco
#psyco.full()

########################
def get_program_path():
    module_file = __file__
    module_dir = os.path.split(os.path.abspath(module_file))[0]
    program_folder = os.path.abspath(module_dir)
    return program_folder

os.chdir(get_program_path())
sys.path.append(get_program_path())
########################


class ApplicationWindow(wx.Frame):
    """
    An application window that allows the user to open multiple GuiProjects
    simultaneously.
    """
    def __init__(self,*args,**keywords):
        wx.Frame.__init__(self,*args,**keywords)
        self.SetDoubleBuffered(True)
        self.notebook=notebookctrl.NotebookCtrl(self,-1,style=notebookctrl.NC_TOP)


        self.gui_projects=[]

        filemenu=wx.Menu()
        new_menu_button = filemenu.Append(-1 ,"&New"," New")
        exit_menu_button = filemenu.Append(-1 ,"E&xit"," Close the program")
        self.Bind(wx.EVT_MENU, self.on_new, new_menu_button)
        self.Bind(wx.EVT_MENU, self.exit, exit_menu_button)        
        menubar=wx.MenuBar()
        menubar.Append(filemenu,"&File")
        #menubar.Append(stuffmenu,"&Stuff")
        #menubar.Append(nodemenu,"&Node")
        self.SetMenuBar(menubar)
        self.CreateStatusBar()
        toolbar = self.CreateToolBar()
        new_tool = toolbar.AddSimpleTool(-1, wx.Bitmap(os.path.join("images","new.png"), wx.BITMAP_TYPE_ANY),"New", " Create a new file")
        toolbar.AddSeparator()
        done_tool = toolbar.AddSimpleTool(-1, wx.Bitmap(os.path.join("images","check.png"), wx.BITMAP_TYPE_ANY),"Done editing", " Done editing")
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.on_new, new_tool)
        self.Bind(wx.EVT_TOOL, self.done_editing, done_tool)

        """
        self.Bind(EVT_RUN_BACKGROUND, self.on_run_background)

        event = wx.PyEvent()
        event.SetEventType(wxEVT_RUN_BACKGROUND)
        wx.PostEvent(self, event)

        self.run_background_block=False
        """

        self.background_timer = threadtimer.ThreadTimer(self)
        self.background_timer.start(150)
        self.Bind(threadtimer.EVT_THREAD_TIMER, self.sync_crunchers)

        self.Show()

    def add_gui_project(self,gui_project):
        self.gui_projects.append(gui_project)
        self.notebook.AddPage(gui_project.main_window,"zort!",select=True)

    """
    def delete_gui_project(self,gui_project):
        I did this wrong.
        self.gui_projects.remove(gui_project)
        self.notebook.AddPage(gui_project.main_window,"zort!")
        self.notebook.DeletePage(0)
        del gui_project
    """

    def exit(self,e):
        self.background_timer.stop()
        self.Close()

    def done_editing(self,e=None):
        gui_project=self.get_active_gui_project()
        gui_project.done_editing()

    def get_active_gui_project(self):
        selected_tab=self.notebook.GetPage(self.notebook.GetSelection())
        for gui_project in self.gui_projects:
            if gui_project.main_window==selected_tab:
                return gui_project
        raise StandardError("No GuiProject selected.")

    def on_new(self,e):
        dialog=customwidgets.SimpackSelectionDialog(self,-1)
        if dialog.ShowModal() == wx.ID_OK:
            simpack=dialog.get_simpack_selection()
        else:
            dialog.Destroy()
            return
        dialog.Destroy()

        gui_project=guiproject.GuiProject(simpack,self.notebook)
        self.add_gui_project(gui_project)

    def sync_crunchers(self, e=None):
        """
        A function that calls `sync_crunchers` for all the
        open GuiProjects.
        """
        for gui_project in self.gui_projects:
            gui_project.sync_crunchers()



def main():
    app = wx.PySimpleApp()
    my_app_win=ApplicationWindow(None, -1, "GarlicSim", size=(600,600))

    """
    import cProfile
    cProfile.run("app.MainLoop()")
    """
    app.MainLoop()



if __name__=="__main__":
    main()