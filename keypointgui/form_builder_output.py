# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 16 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Manual Detection Generator", pos = wx.DefaultPosition, size = wx.Size( 1314,988 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 400,400 ), wx.DefaultSize )
		self.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		
		main_size = wx.BoxSizer( wx.VERTICAL )
		
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.tool_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		button_sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.button_panel = wx.Panel( self.tool_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer111 = wx.BoxSizer( wx.VERTICAL )
		
		self.interpolation_label = wx.StaticText( self.button_panel, wx.ID_ANY, u"Rendering", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.interpolation_label.Wrap( -1 )
		self.interpolation_label.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer111.Add( self.interpolation_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		interpolation_choiceChoices = [ u"nearest", u"linear", u"area", u"cubic", u"lanczos4" ]
		self.interpolation_choice = wx.Choice( self.button_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, interpolation_choiceChoices, 0 )
		self.interpolation_choice.SetSelection( 3 )
		bSizer111.Add( self.interpolation_choice, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.button_panel.SetSizer( bSizer111 )
		self.button_panel.Layout()
		bSizer111.Fit( self.button_panel )
		button_sizer.Add( self.button_panel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticline11 = wx.StaticLine( self.tool_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		button_sizer.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer1111 = wx.BoxSizer( wx.VERTICAL )
		
		self.alignment_label = wx.StaticText( self.tool_panel, wx.ID_ANY, u"Alignment", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.alignment_label.Wrap( -1 )
		self.alignment_label.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer1111.Add( self.alignment_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.align_original_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Original", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1111.Add( self.align_original_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.align_left_to_right_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Left --> Right", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1111.Add( self.align_left_to_right_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.align_right_to_left_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Right --> Left", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1111.Add( self.align_right_to_left_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.sync_zooms_checkbox = wx.CheckBox( self.tool_panel, wx.ID_ANY, u"Sync Zooms", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sync_zooms_checkbox.SetValue(True) 
		bSizer1111.Add( self.sync_zooms_checkbox, 0, wx.ALL, 5 )
		
		self.alignment_label1 = wx.StaticText( self.tool_panel, wx.ID_ANY, u"Alignment", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.alignment_label1.Wrap( -1 )
		self.alignment_label1.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer1111.Add( self.alignment_label1, 0, wx.ALL, 5 )
		
		
		button_sizer.Add( bSizer1111, 0, wx.EXPAND, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.tool_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		button_sizer.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.clear_last_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Clear Last", wx.DefaultPosition, wx.DefaultSize, 0 )
		button_sizer.Add( self.clear_last_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.clear_all_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Clear All", wx.DefaultPosition, wx.DefaultSize, 0 )
		button_sizer.Add( self.clear_all_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self.tool_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		button_sizer.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.finish_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Finish", wx.DefaultPosition, wx.DefaultSize, 0 )
		button_sizer.Add( self.finish_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.cancel_button = wx.Button( self.tool_panel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		button_sizer.Add( self.cancel_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		self.tool_panel.SetSizer( button_sizer )
		self.tool_panel.Layout()
		button_sizer.Fit( self.tool_panel )
		bSizer14.Add( self.tool_panel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		image1_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		image1_navigation_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image1_nav_panel_title = wx.StaticText( self, wx.ID_ANY, u"Image 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.image1_nav_panel_title.Wrap( -1 )
		self.image1_nav_panel_title.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		image1_navigation_bsizer.Add( self.image1_nav_panel_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.image1_nav_panel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.image1_nav_panel.SetScrollRate( 5, 5 )
		image1_navigation_bsizer.Add( self.image1_nav_panel, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		image1_bsizer.Add( image1_navigation_bsizer, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		image1_zoom_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image1_zoom_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		image1_zoom_bsizer.Add( self.image1_zoom_panel, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.zoom1_label = wx.StaticText( self, wx.ID_ANY, u"Zoom", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.zoom1_label.Wrap( -1 )
		self.zoom1_label.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer10.Add( self.zoom1_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.zoom1_spin_button = wx.SpinButton( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 20,-1 ), wx.SP_WRAP )
		bSizer10.Add( self.zoom1_spin_button, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.zoom1_txt = wx.StaticText( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.zoom1_txt.Wrap( -1 )
		self.zoom1_txt.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer10.Add( self.zoom1_txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		image1_zoom_bsizer.Add( bSizer10, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		image1_bsizer.Add( image1_zoom_bsizer, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer14.Add( image1_bsizer, 1, wx.EXPAND, 5 )
		
		image2_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		image2_navigation_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image2_nav_panel_title = wx.StaticText( self, wx.ID_ANY, u"Image 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.image2_nav_panel_title.Wrap( -1 )
		self.image2_nav_panel_title.SetFont( wx.Font( 18, 70, 90, 92, False, wx.EmptyString ) )
		
		image2_navigation_bsizer.Add( self.image2_nav_panel_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.image2_nav_panel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.image2_nav_panel.SetScrollRate( 5, 5 )
		image2_navigation_bsizer.Add( self.image2_nav_panel, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		image2_bsizer.Add( image2_navigation_bsizer, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		image2_zoom_bsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image2_zoom_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		image2_zoom_bsizer.Add( self.image2_zoom_panel, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		bSizer101 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.zoom2_label = wx.StaticText( self, wx.ID_ANY, u"Zoom", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE )
		self.zoom2_label.Wrap( -1 )
		self.zoom2_label.SetFont( wx.Font( 12, 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer101.Add( self.zoom2_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.zoom2_spin_button = wx.SpinButton( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 20,-1 ), wx.SP_WRAP )
		bSizer101.Add( self.zoom2_spin_button, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.zoom2_txt = wx.StaticText( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.zoom2_txt.Wrap( -1 )
		self.zoom2_txt.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer101.Add( self.zoom2_txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		image2_zoom_bsizer.Add( bSizer101, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		image2_bsizer.Add( image2_zoom_bsizer, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer14.Add( image2_bsizer, 1, wx.EXPAND, 5 )
		
		
		main_size.Add( bSizer14, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( main_size )
		self.Layout()
		self.status_bar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.m_menubar1 = wx.MenuBar( 0 )
		self.menu_file = wx.Menu()
		self.menu_item_load_left_image = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Load Left Image", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_item_load_left_image )
		
		self.menu_item_load_right_image = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Load Right Image", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_item_load_right_image )
		
		self.menu_item_save_points = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Save Points", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_item_save_points )
		
		self.menu_item_save_left_to_right_homography = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Save Left->Right Homography", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_item_save_left_to_right_homography )
		
		self.menu_item_save_right_to_left_homography = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Save Right->Left Homography", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_item_save_right_to_left_homography )
		
		self.exit_menu_item = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.exit_menu_item )
		
		self.m_menubar1.Append( self.menu_file, u"File" ) 
		
		self.menu_help = wx.Menu()
		self.menu_item_about = wx.MenuItem( self.menu_help, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_help.AppendItem( self.menu_item_about )
		
		self.m_menubar1.Append( self.menu_help, u"Help" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.align_original_button.Bind( wx.EVT_BUTTON, self.on_align_original )
		self.align_left_to_right_button.Bind( wx.EVT_BUTTON, self.on_align_left_to_right )
		self.align_right_to_left_button.Bind( wx.EVT_BUTTON, self.on_align_right_to_left )
		self.clear_last_button.Bind( wx.EVT_BUTTON, self.on_clear_last_button )
		self.clear_all_button.Bind( wx.EVT_BUTTON, self.on_clear_all_button )
		self.finish_button.Bind( wx.EVT_BUTTON, self.on_finish_button )
		self.cancel_button.Bind( wx.EVT_BUTTON, self.on_cancel_button )
		self.Bind( wx.EVT_MENU, self.on_load_left_image, id = self.menu_item_load_left_image.GetId() )
		self.Bind( wx.EVT_MENU, self.on_load_right_image, id = self.menu_item_load_right_image.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_points, id = self.menu_item_save_points.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_left_to_right_homography, id = self.menu_item_save_left_to_right_homography.GetId() )
		self.Bind( wx.EVT_MENU, self.on_save_right_to_left_homography, id = self.menu_item_save_right_to_left_homography.GetId() )
		self.Bind( wx.EVT_MENU, self.on_close_button, id = self.exit_menu_item.GetId() )
		self.Bind( wx.EVT_MENU, self.on_menu_item_about, id = self.menu_item_about.GetId() )
	
	def __del__( self ):
		# Disconnect Events
		self.align_original_button.Unbind( wx.EVT_BUTTON, None )
		self.align_left_to_right_button.Unbind( wx.EVT_BUTTON, None )
		self.align_right_to_left_button.Unbind( wx.EVT_BUTTON, None )
		self.clear_last_button.Unbind( wx.EVT_BUTTON, None )
		self.clear_all_button.Unbind( wx.EVT_BUTTON, None )
		self.finish_button.Unbind( wx.EVT_BUTTON, None )
		self.cancel_button.Unbind( wx.EVT_BUTTON, None )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_load_left_image.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_load_right_image.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_save_points.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_save_left_to_right_homography.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_save_right_to_left_homography.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.exit_menu_item.GetId() )
		self.Unbind( wx.EVT_MENU, id = self.menu_item_about.GetId() )
	
	
	# Virtual event handlers, overide them in your derived class
	def on_align_original( self, event ):
		event.Skip()
	
	def on_align_left_to_right( self, event ):
		event.Skip()
	
	def on_align_right_to_left( self, event ):
		event.Skip()
	
	def on_clear_last_button( self, event ):
		event.Skip()
	
	def on_clear_all_button( self, event ):
		event.Skip()
	
	def on_finish_button( self, event ):
		event.Skip()
	
	def on_cancel_button( self, event ):
		event.Skip()
	
	def on_load_left_image( self, event ):
		event.Skip()
	
	def on_load_right_image( self, event ):
		event.Skip()
	
	def on_save_points( self, event ):
		event.Skip()
	
	def on_save_left_to_right_homography( self, event ):
		event.Skip()
	
	def on_save_right_to_left_homography( self, event ):
		event.Skip()
	
	def on_close_button( self, event ):
		event.Skip()
	
	def on_menu_item_about( self, event ):
		event.Skip()
	

