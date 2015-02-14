# board.py
# -*- coding: utf-8 -*-

# note taking class for notes.py

import wx
from boardbase import BoardBase
from card import *


######################
# Board Class
######################

class Board(BoardBase):
    CARD_PADDING = BoardBase.CARD_PADDING
    HORIZONTAL = BoardBase.HORIZONTAL
    VERTICAL   = BoardBase.VERTICAL

    def __init__(self, parent, id=wx.ID_ANY, pos=(0,0), size=(20,20)):
        super(Board, self).__init__(parent, size=size, pos=pos)

        self.menu_position = (0, 0)

        # UI setup
        self.InitMenu()

        
    ### Auxiliary functions

    def InitMenu(self):
        # make menu
        menu = wx.Menu()
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # edit actions
        past_it = wx.MenuItem(menu, wx.ID_PASTE, "Paste")
        self.Bind(wx.EVT_MENU, self.OnPaste, past_it)

        # insert actions
        cont_it = wx.MenuItem(menu, wx.ID_ANY, "Insert Content")
        self.Bind(wx.EVT_MENU, self.OnInsertContent, cont_it)

        head_it = wx.MenuItem(menu, wx.ID_ANY, "Insert Header")
        self.Bind(wx.EVT_MENU, self.OnInsertHeader, head_it)
        
        img_it = wx.MenuItem(menu, wx.ID_ANY, "Insert Image")
        self.Bind(wx.EVT_MENU, self.OnInsertImg, img_it)
        
        # tab actions
        close_it = wx.MenuItem(menu, wx.ID_ANY, "Close")
        self.Bind(wx.EVT_MENU, self.OnClose, close_it)

        menu.AppendItem(past_it)
        menu.AppendItem(cont_it)
        menu.AppendItem(head_it)
        menu.AppendItem(img_it)
        menu.AppendSeparator()
        menu.AppendItem(close_it)        

        self.menu = menu

        
    ### Callbacks

    def OnRightDown(self, ev):
        self.menu_position = ev.GetPosition()
        self.PopupMenu(self.menu, ev.GetPosition())

    def OnPaste(self, ev):
        self.PasteFromClipboard(self.menu_position)

    def OnInsertContent(self, ev):
        self.PlaceNewCard("Content", pos=self.menu_position)

    def OnInsertHeader(self, ev):
        self.PlaceNewCard("Header", pos=self.menu_position)

    def OnInsertImg(self, ev):
        self.PlaceNewCard("Image", pos=self.menu_position)

    def OnClose(self, ev):
        # should close tab
        pass
