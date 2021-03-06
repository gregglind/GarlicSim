# Copyright 2009 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

import wx
import wx.lib.scrolledpanel as scrolled

'''
Defines the BoardWidget class.
'''

class BoardWidget(scrolled.ScrolledPanel):
    '''
    Widget for displaying a Life board.
    '''
    def __init__(self, parent, id, gui_project, *args, **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, id,
                                        style=wx.SUNKEN_BORDER, *args,
                                        **kwargs)
        self.SetupScrolling()
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)

        self.gui_project = gui_project
        self.border_width = 1
        self.square_size = 7
        self.board = None

        
    def unscreenify(self, x, y):
        '''Translate screen coordinates to board coordinates.'''
        if self.board is None:
            return None
        screen_tuple = self.CalcUnscrolledPosition(x, y)
        result = [(thing // (self.border_width + self.square_size)) for
                  thing in screen_tuple]
        if (0 <= result[0] < self.board.width) and \
           (0 <= result[1] < self.board.height):
            return tuple(result)
        else:
            return None

    def set_board(self, board):
        '''Set the board to be displayed.'''
        self.board = board
        self.Refresh()

    def on_paint(self, e=None):
        '''Paint event handler.'''
        
        board = self.board
        dc = wx.PaintDC(self)

        if board is None:
            dc.Destroy()
            return

        white_brush = wx.Brush("White")
        black_brush = wx.Brush("Black")
        rectangles = []
        brushes = []
        for x in xrange(board.width):
            for y in xrange(board.height):
                rectangles.append([(self.square_size + self.border_width) * x,
                                   (self.square_size + self.border_width) * y,
                                   self.square_size,
                                   self.square_size])
                brushes.append(black_brush if board.get(x,y) is True
                               else white_brush)


        for rect in rectangles:
            (rect[0], rect[1]) = self.CalcScrolledPosition((rect[0], rect[1]))


        transparent_pen = wx.Pen('#000000', 0, wx.TRANSPARENT)


        dc.DrawRectangleList(rectangles, transparent_pen, brushes)
        dc.Destroy()

        self.SetVirtualSize(
            (
                board.width * (self.square_size + self.border_width),
                board.height * (self.square_size + self.border_width)
            )
        )



    def on_size(self, e=None):
        '''Refresh the widget.'''
        self.Refresh()

    def on_mouse_event(self, e):
        '''Mouse event handler.'''
        
        if e.LeftDown():
            pos = e.GetPositionTuple()
            thing = self.unscreenify(*pos)
            if thing is not None:
                (x, y) = thing
                old_value = self.board.get(x,y)
                new_value = (not old_value)

                new_state = self.gui_project.editing_state()
                new_board = new_state.board
                new_board.set(x, y, new_value)


        self.Refresh()
