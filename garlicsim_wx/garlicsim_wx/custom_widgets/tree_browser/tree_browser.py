# Copyright 2009 Ram Rachum. No part of this program may be used, copied or
# distributed without explicit written permission from Ram Rachum.

'''
This module defines the TreeBrowser class. See its documentation for more info.
'''
#todo: I think the refresh should be made more efficient


import os
from math import *

import pkg_resources
import wx
from wx.lib.scrolledpanel import ScrolledPanel

import garlicsim_wx.general_misc.vectorish as vectorish
import garlicsim.data_structures

from . import images as __images_package
images_package = __images_package.__name__

connector_length = 10 # length of connecting line between elements


class TreeBrowser(ScrolledPanel):
    '''
    A widget for browsing a garlicsim.data_structures.Tree.
    '''
    def __init__(self, parent, id, gui_project=None, *args, **kwargs):
        ScrolledPanel.__init__(self, parent, id, size=(-1, 100),
                               style=wx.SUNKEN_BORDER)

        self.SetupScrolling()
        #self.SetScrollRate(20,20)
        #self.sizer=wx.BoxSizer(wx.VERTICAL)
        #self.panel=wx.StaticBitmap(self,-1,wx.Bitmap("images\\snail.gif", wx.BITMAP_TYPE_ANY))#wx.Panel(self,-1,size=(-1,200))#wx.TextCtrl(self, -1, size=(-1,200), style=wx.TE_MULTILINE)
        #self.panel=wx.Panel(self,-1,size=(-1,100))
        #self.sizer.Add(self.panel,1,wx.EXPAND)
        #self.SetSizer(self.sizer)
        #self.EnableScrolling(True, True)
        #self.SetScrollbars(5, 30, 1055, 40)
        #self.sizer.Fit(self)
        #self.Centre()
        #self.SetVirtualSize((1000,1000))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)

        self.gui_project = gui_project
        self.clickable_map = {}

    def on_paint(self, e=None):
        '''Refresh the tree browser.'''

        if self.gui_project is None or \
           self.gui_project.project.tree is None or \
           len(self.gui_project.project.tree.roots) == 0:
            
            return


        pen = wx.Pen("Black", 1, wx.SOLID)
        pen.SetCap(wx.CAP_PROJECTING)
        pen.SetJoin(wx.JOIN_ROUND)

        dc = NiftyPaintDC(self, self.gui_project,
                          self.CalcScrolledPosition((0, 0)))
        
        (self.clickable_map, (width, height)) = \
            dc.draw_tree(self.gui_project.project.tree)
        
        self.SetVirtualSize((width,height))
        dc.Destroy()

    def on_size(self, e=None):
        self.Refresh()

    def on_mouse_event(self, e):
        #(x,y)=self.CalcUnscrolledPosition(e.GetPositionTuple())

        (x, y) = e.GetPositionTuple()
        
        if e.LeftDClick():
            self.gui_project.toggle_playing()


        if e.LeftIsDown():
            thing = self.search_map(x,y)
            #print(thing)
            if thing is None:
                #maybe deselect?
                pass
            else:
                self.gui_project.set_active_node(thing)
                
        if e.RightDown():
            self.gui_project.stop_playing()
            thing = self.search_map(x,y)
            if thing is None:
                #Deselect!
                pass
            else:
                self.gui_project.set_active_node(thing)
                
            self.PopupMenu(self.gui_project.get_node_menu(), e.GetPosition())


    def search_map(self, x, y):
        for key in self.clickable_map:
            (a, b, c, d) = key
            if (a <= x <= c) and (b <= y <= d):
                thing = self.clickable_map[key]
                if isinstance(thing, garlicsim.data_structures.Block):
                    ratio = (x - a) / float(c - a)
                    index = int(round(ratio*(len(thing)-1)))
                    return thing[index]
                else:
                    return thing
        return None



class NiftyPaintDC(wx.PaintDC):
    '''A PaintDC used to paint the tree in a tree browser.'''
    
    def __init__(self, window, gui_project, origin, *args, **kwargs):
        wx.PaintDC.__init__(self, window, *args, **kwargs)
        self.gui_project = gui_project
        self.origin = origin
        
        elements_raw = {
            
            'Untouched': 'graysquare.png',
            'Touched': 'graystar.png',
            'Block': 'grayblock.png',
            'Active Untouched': 'orangesquare.png',
            'Active Touched': 'orangestar.png',
            'Active Block': 'orangeblock.png',
        }
        
        self.elements = {}
        for key in elements_raw:
            file_name = pkg_resources.resource_filename(images_package,
                                                        elements_raw[key])
            self.elements[key] = wx.Bitmap(file_name, wx.BITMAP_TYPE_ANY)

    def draw_sub_tree(self, point, tree, start):
        make_block_stripe = False
        if isinstance(start, garlicsim.data_structures.Block):
            type = "Block"
            kids = start[-1].children
            if start == self.active_soft_block:
                make_block_stripe = True
                type = "Active " + type
        elif isinstance(start, garlicsim.data_structures.Node):
            kids = start.children
            if start.touched:
                type = "Touched"
            else:
                type = "Untouched"
            if start == self.active_soft_block:
                type = "Active " + type
        else:
            raise StandardError


        if make_block_stripe is True:

            bitmap = self.elements["Block"]
            self.DrawBitmapPoint(bitmap, point, useMask=True)
            bitmap_size = bitmap.GetSize()
            second_bitmap = self.elements[type]

            slice = [None, None]
            length = float(len(start))
            slice[0] = start.index(self.active_node) / length
            slice[1] = slice[0] + (1 / length)

            screen_slice = [
                floor(point[0] + 2 + (bitmap_size[0] - 4) * slice[0]),
                ceil(point[0] + 2 + (bitmap_size[0] - 4) * slice[1])
            ]
            region = wx.Region(screen_slice[0], point[1],
                               screen_slice[1] - screen_slice[0],
                               bitmap_size[1])
            
            self.SetClippingRegionAsRegion(region)
            self.DrawBitmapPoint(second_bitmap, point, useMask=True)
            self.DestroyClippingRegion()

        else:
            bitmap = self.elements[type]
            self.DrawBitmapPoint(bitmap, point, useMask=True)
            bitmap_size = bitmap.GetSize()

        temp = (point[0],
                point[1],
                point[0] + bitmap_size[0],
                point[1] + bitmap_size[1])
        
        self.clickable_map[temp] = start
        del temp



        last_height = 0
        total_height = 0
        self_width = bitmap_size[0] + connector_length
        max_width = self_width
        line_start = vectorish.add(
            point,
            (
                bitmap_size[0] - 1,
                bitmap_size[1] // 2
            )
        )
        
        for kid in kids:
            line_end = vectorish.add(
                point,
                (
                    self_width + 1,
                 total_height + bitmap_size[1] // 2
                )
            )
            
            temp = vectorish.add(point, (self_width, total_height))
            (new_width, new_height) = \
                self.draw_sub_tree(temp, tree, kid.soft_get_block())
            del temp
            self.DrawLinePoint(line_start, line_end)
            max_width = max(max_width, self_width + new_width)
            total_height += new_height

        return (
            max_width,
            max(
                total_height,
                bitmap_size[1] + connector_length
            )
        )

    def draw_tree(self, tree):
        '''
        Draw the tree.
        
        This will only use the part of the tree that springs from the first
        root!
        '''

        self.clickable_map = {}
        self.active_node = self.gui_project.active_node
        try:
            self.active_soft_block = self.active_node.soft_get_block()
        except AttributeError:
            self.active_soft_block = None

        size = self.draw_sub_tree(
            vectorish.add(
                (connector_length, connector_length),
                self.origin
                ),
            tree,
            tree.roots[0].soft_get_block()
        )
        
        (width, height) = vectorish.add(size, (connector_length, connector_length))
        return (self.clickable_map, (width, height))


'''

Maybe I'll use this sometime:

                        "Selected Untouched": wx.Bitmap("images\\bluesquare.png", wx.BITMAP_TYPE_ANY),    \
                       "Selected Touched": wx.Bitmap("images\\bluestar.png", wx.BITMAP_TYPE_ANY),    \
                       "Selected Block": wx.Bitmap("images\\blueblock.png", wx.BITMAP_TYPE_ANY),    \
'''


'''

Maybe I'll use this sometime:

class Object(object):
    def __init__(self,*args,**kwargs):
        pass

class StateContainer(Object):
    def __init__(self,parent=None,connector_class=None,*args,**kwargs):
        Object.__init__(self,*args,**kwargs)
        assert [x for x in [parent,connector_class] if x==None]!=[None]
        self.parent=parent
        connector=connector_class(parent,self)

        self.children={} # {child: connector}



class Node(StateContainer):
    def __init__(self,*args,**kwargs):
        StateContainer.__init__(self,*args,**kwargs)
        pass

class TouchedNode(Node):
    def __init__(self,*args,**kwargs):
        Node.__init__(self,*args,**kwargs)
        pass

class UntouchedNode(Node):
    def __init__(self,*args,**kwargs):
        Node.__init__(self,*args,**kwargs)
        pass

class Block(StateContainer):
    def __init__(self,*args,**kwargs):
        StateContainer.__init__(self,*args,**kwargs)
        pass

class Connector(Object):
    def __init__(self,parent,child,*args,**kwargs):
        Object.__init__(self,*args,**kwargs)
        parent.children[child]=self
'''
