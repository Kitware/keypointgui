#!/usr/bin/env python
from __future__ import division, print_function
import wx
from wx.lib.wordwrap import wordwrap
import form_builder_output
import cv2
import numpy as np
from wxpython_gui.wx_elements import ImagePanelManager
import os

license_str = ''.join(['Copyright 2017 by Kitware, Inc.\n',
'All rights reserved.\n\n',
'Redistribution and use in source and binary forms, with or without ',
'modification, are permitted provided that the following conditions are met:',
'\n\n',
'* Redistributions of source code must retain the above copyright notice, ',
'this list of conditions and the following disclaimer.',
'\n\n',
'* Redistributions in binary form must reproduce the above copyright notice, ',
'this list of conditions and the following disclaimer in the documentation ',
'and/or other materials provided with the distribution.',
'\n\n',
'* Neither name of Kitware, Inc. nor the names of any contributors may be ',
'used to endorse or promote products derived from this software without ',
'specific prior written permission.',
'\n\n',
'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ',
'\'AS IS\' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED ',
'TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR ',
'PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE ',
'LIABLE FORANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR ',
'CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF ',
'SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS ',
'INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN ',
'CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ',
'ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE ',
'POSSIBILITY OF SUCH DAMAGE.'])

license_str = 'Unreleased: Squad-X'


class NavigationPanelImage(ImagePanelManager):
    """The left navigation panel used to select where to center the zoom panel.
    
    Attributes:
    :param align_homography: Homography that "corrects" the image. It takes 
        image coordinates from the raw image and returns the corrected image 
        coordinates.
        
    """
    def __init__(self, wx_panel, image, zoom_panel_image, status_bar=None):
        """
        :param wx_panel: Panel to add the image to.
        :type wx_panel: wx.Panel
        
        :param image: Image.
        :type raw_image: numpy.ndarray | None
        
        :param zoom_panel_image: The instance of ZoomPanelImage associated with
        the navigation pane.
        :type zoom_panel_image: ZoomPanelImage
        """
        super(self.__class__, self).__init__(wx_panel, image, 
             status_bar=status_bar)
        self.zoom_panel_image = zoom_panel_image
        self.align_homography = np.identity(3)
        self.corrected_img_shape = self.raw_image.shape[:2]
        
        # When the zoom panel changes, make sure the navigation panel is 
        # redrawn.
        self.zoom_panel_image.wx_panel.Bind(wx.EVT_PAINT, self.refresh)
        
    def update_homography(self):
        #print('on_size')
        panel_width, panel_height = self.wx_panel.GetSize()
        im_height, im_width = self.raw_image.shape[:2]
        
        if False:
            print('Panel Size ({}, {})'.format(panel_width, panel_height))
            print('Original Image Size ({}, {})'.format(im_width, im_height))
        
        im_height, im_width = self.corrected_img_shape
        
        if im_width/im_height > panel_width/panel_height:
            # Side edges of image should hit the edges of the panel.
            s = panel_width/im_width
            ty = (panel_height - s*im_height)/2
            self.homography = np.dot(np.array([[s,0,0],[0,s,ty],[0,0,1]]),
                                     self.align_homography)
        else:
            # Top edges of image should hit the edges of the panel.
            s = panel_height/im_height
            tx = (panel_width-s*im_width)/2
            self.homography = np.dot(np.array([[s,0,tx],[0,s,0],[0,0,1]]),
                                              self.align_homography)
        
        if False:
            print('Corrected Image Size ({}, {})'.format(im_width, im_height))
            print('Homography', self.homography)
    
    def process_clicked_point(self, pos, button):
        self.zoom_panel_image.process_clicked_point(pos, 1)
        # No need to refresh, any changes to the zoom panel will automatically 
        # trigger a refresh of the navigation panel.
    
    def draw_overlay(self, dc):
        """
        """
        dc.SetPen(wx.Pen(wx.RED, 2))
        
        # Draw zoom window
        w, h = self.zoom_panel_image.wx_panel.GetSize()
        pts = np.array([[0,w,w,0,0],[0,0,h,h,0],[1,1,1,1,1]])
        pts = np.dot(self.zoom_panel_image.inverse_homography, pts)
        pts = np.dot(self.homography, pts)
        pts = pts[:2]/pts[2]
        for i in range(4):
            dc.DrawLine(pts[0,i], pts[1,i], pts[0,i+1], pts[1,i+1])


class ZoomPanelImage(ImagePanelManager):
    """The right navigation panel used to select where to center the 
    zoom panel.
    
    """
    def __init__(self, wx_panel, image, zoom=400, center=None, 
                 zoom_spin_button=None, zoom_label=None,
                 click_callback=None, status_bar=None):
        """
        :param wx_panel: Panel to add the image to.
        :type wx_panel: wx.Panel
        
        :param image: Image.
        :type raw_image: numpy.ndarray | None
        
        :param zoom: Percent zoom.
        :type zoom: float
        
        :param center: Full-image coordinates corresponding to the center of 
            the zoom panel view.
        :type center: 2-array of float
        
        :param click_callback: Function to call when left-mouse is clicked. It
            should expect one arguement pos (the point clicked).
            
        s"""
        super(self.__class__, self).__init__(wx_panel, image, 
             status_bar=status_bar)
            
        if center is None and self.raw_image is not None:
            center = np.array(self.raw_image.shape[:2][::-1])/2
        
        self.align_homography = np.identity(3)
        self.corrected_img_shape = self.raw_image.shape[:2]
        
        self.zoom_spin_button = zoom_spin_button
        self.zoom_label = zoom_label
        
        self._center = center
        self.click_callback = click_callback
        
        self.handle_updated_zoom(zoom)
        
        self.zoom_spin_button.Bind(wx.EVT_SPIN_DOWN, self.on_zoom_down)
        self.zoom_spin_button.Bind(wx.EVT_SPIN_UP, self.on_zoom_up)
        self.wx_panel.Bind(wx.EVT_MOUSEWHEEL, self.on_zoom_mouse_wheel)
        
    def set_zoom(self, zoom):
        """
        :param zoom: Zoom percentage.
        :type zoom: float
        """
        self._zoom = zoom
        self.update_all()
    
    def set_center(self, center):
        """
        :param center: Location for the zoom center in the original image's coordinates.
        :type center: 2-array
        """
        self._center = center
        self.update_all()
    
    def update_homography(self):
        if self._zoom is None:
            return None
        
        #print('on_size')
        panel_width, panel_height = self.wx_panel.GetSize()
        im_height, im_width = self.raw_image.shape[:2]
        #print('Panel Size ({}, {})'.format(panel_width, panel_height))
        #print('Image Size ({}, {})'.format(im_width, im_height))
        
        s = self._zoom/100
        
        # Get the coordinate in the "corrected" image of the clicked center.
        center = np.dot(self.align_homography, [self._center[0], 
                                                self._center[1], 1])
        center = center[:2]/center[2]
        
        tx = panel_width/2-s*center[0]
        ty = panel_height/2-s*center[1]
        h_zoom = np.array([[s,0,tx],[0,s,ty],[0,0,1]])
        self.homography = np.dot(h_zoom, self.align_homography)
    
    def process_clicked_point(self, pos, button):
        self.click_callback(pos, button)
    
    def on_zoom_mouse_wheel(self, event=None):
        val = event.GetWheelRotation()
        if event.ShiftDown():
            change = 1.1
        else:
            change = 1.01
            
        if val > 0:
            self.on_zoom_up(change=change)
        if val < 0:
            self.on_zoom_down(change=change)
        
    def on_zoom_up(self, event=None, change=1.02):
        zoom = np.minimum(self._zoom*change, 2000)
        self.handle_updated_zoom(zoom)
    
    def on_zoom_down(self, event=None, change=1.02):
        zoom = np.maximum(self._zoom/change, 10)
        self.handle_updated_zoom(zoom)
    
    def handle_updated_zoom(self, zoom):
        self.zoom_label.SetLabel('{}%'.format(int(np.round(zoom))))
        self.set_zoom(zoom)
    

class MainFrame(form_builder_output.MainFrame):
    #constructor
    def __init__(self, parent, image1, image2, title1='Image 1', 
                 title2='Image 2', passback_dict={'points',None}, 
                 initial_zoom=400, window_title='Manual Image Registration'):
        """
        :param image1_topic: First image topic name.
        :type image_topics: list of str
        
        :param image1_topic: First image topic name.
        :type image_topics: list of str
        
        """
        
        #initialize parent class
        form_builder_output.MainFrame.__init__(self, parent)
        self.SetTitle(window_title)
        self.zoom = initial_zoom
        self.image1 = image1
        self.image2 = image2
        self.click_state = 0
        assert isinstance(passback_dict, dict)
        self.passback_dict = passback_dict
        
        if title1 is not None:
            self.image1_nav_panel_title.SetLabel(title1)
        
        if title2 is not None:
            self.image2_nav_panel_title.SetLabel(title2)
        
        # Image 1 views.
        self.zoom_panel_image1 = ZoomPanelImage(self.image1_zoom_panel, 
                                        self.image1, 
                                        zoom_spin_button=self.zoom1_spin_button,
                                        zoom_label=self.zoom1_txt,
                                        click_callback=self.on_clicked_point1,
                                        status_bar=self.status_bar)
        
        self.nav_panel_image1 = NavigationPanelImage(self.image1_nav_panel, 
                                                     self.image1, 
                                                     self.zoom_panel_image1,
                                                     self.status_bar)
        
        # Image 2 views.
        self.zoom_panel_image2 = ZoomPanelImage(self.image2_zoom_panel, 
                                        self.image2, 
                                        zoom_spin_button=self.zoom2_spin_button,
                                        zoom_label=self.zoom2_txt,
                                        click_callback=self.on_clicked_point2,
                                        status_bar=self.status_bar)
        
        self.nav_panel_image2 = NavigationPanelImage(self.image2_nav_panel, 
                                                     self.image2, 
                                                     self.zoom_panel_image2,
                                                     self.status_bar)
        
        # Apply the current default interpolation.
        self.on_interpolation_update(None)
        
        # Interpolation choice bindings.
        self.interpolation_choice.Bind(wx.EVT_CHOICE,
                                       self.on_interpolation_update)
        
        # Grey out check box until alignment has been performed.
        self.sync_zooms_checkbox.SetValue(False)
        self.sync_zooms_checkbox.Enable(False)
        
        if self.passback_dict['points'] is not None:
            points = self.passback_dict['points']
            pts1 = points[:,:2]
            pts2 = points[:,2:]
            self.nav_panel_image1.set_red_points(pts1)
            self.zoom_panel_image1.set_red_points(pts1)
            self.nav_panel_image2.set_red_points(pts2)
            self.zoom_panel_image2.set_red_points(pts2)
        
        self.Bind(wx.EVT_CLOSE, self.when_closed)
        
        self.Show()
        self.SetMinSize(self.GetSize())
    
    def on_interpolation_update(self, event):
        interp = self.interpolation_choice.GetSelection()
        
        # Image 1
        self.zoom_panel_image1.set_interpolation(interp)
        self.zoom_panel_image1.update_all()
        self.nav_panel_image1.set_interpolation(interp)
        self.nav_panel_image1.update_all()
        
        # Image 2
        self.zoom_panel_image2.set_interpolation(interp)
        self.zoom_panel_image2.update_all()
        self.nav_panel_image2.set_interpolation(interp)
        self.nav_panel_image2.update_all()
    
    def on_clicked_point1(self, pos, button):
        """
        Clicked on point in image 1.
        
        """
        if button == 1:
            self.zoom_panel_image1.set_center(pos)
            if self.sync_zooms_checkbox.GetValue():
                h1 = self.nav_panel_image1.align_homography
                h2 = self.nav_panel_image2.align_homography
                h = np.dot(h1, np.linalg.inv(h2))
                pos2 = np.dot(h, np.hstack([pos,1]))
                self.zoom_panel_image2.set_center(pos2)
            
            return
        
        if self.click_state == 0:
            # Ready to start a new point pair.
            self.nav_panel_image1.add_blue_point(pos)
            self.zoom_panel_image1.add_blue_point(pos)
            self.click_state = 1
        elif self.click_state == 2:
            # Finish out the click pair.
            point = self.nav_panel_image2.get_blue_points()
            self.nav_panel_image2.clear_blue_points(refresh=False)
            self.zoom_panel_image2.clear_blue_points(refresh=False)
            self.nav_panel_image2.add_red_point(point)
            self.zoom_panel_image2.add_red_point(point)
            self.nav_panel_image1.add_red_point(pos)
            self.zoom_panel_image1.add_red_point(pos)
            self.click_state = 0
        
        #print('Clicked Image Coordinates ({:.2f},{:.2f})'.format(*pos))
    
    def on_clicked_point2(self, pos, button):
        """
        Clicked on point in image 2.
        
        """
        if button == 1:
            self.zoom_panel_image2.set_center(pos)
            if self.sync_zooms_checkbox.GetValue():
                h1 = self.nav_panel_image2.align_homography
                h2 = self.nav_panel_image1.align_homography
                h = np.dot(h1, np.linalg.inv(h2))
                pos2 = np.dot(h, np.hstack([pos,1]))
                self.zoom_panel_image1.set_center(pos2)
            
            return
            
        if self.click_state == 0:
            # Ready to start a new point pair.
            self.nav_panel_image2.add_blue_point(pos)
            self.zoom_panel_image2.add_blue_point(pos)
            self.click_state = 2
        elif self.click_state == 1:
            # Finish out the click pair.
            point = self.nav_panel_image1.get_blue_points()
            self.nav_panel_image1.clear_blue_points(refresh=False)
            self.zoom_panel_image1.clear_blue_points(refresh=False)
            self.nav_panel_image1.add_red_point(point)
            self.zoom_panel_image1.add_red_point(point)
            self.nav_panel_image2.add_red_point(pos)
            self.zoom_panel_image2.add_red_point(pos)
            self.click_state = 0
        
        #print('Clicked Image Coordinates ({:.2f},{:.2f})'.format(*pos))
    
    def on_align_original(self, event):
        panels = [self.nav_panel_image1, self.nav_panel_image2, 
                  self.zoom_panel_image1, self.zoom_panel_image2]
        for panel in panels:
            panel.align_homography = np.identity(3)
            panel.corrected_img_shape = panel.raw_image.shape[:2]
            panel.update_all()
        
        self.sync_zooms_checkbox.SetValue(False)
        self.sync_zooms_checkbox.Enable(False)
        
    def on_align_left_to_right(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()
        if pts1 is None or pts2 is None:
            return
        
        if len(pts1) < 4:
            return
        
        pts1 = pts1.reshape(-1,1,2)
        pts2 = pts2.reshape(-1,1,2)
        H = cv2.findHomography(pts1, pts2)[0]
        
        img_shape = self.nav_panel_image2.raw_image.shape[:2]
        panels = [self.nav_panel_image1, self.zoom_panel_image1]
        for panel in panels:
            panel.align_homography = H
            panel.corrected_img_shape = img_shape
            panel.update_all()
        
        panels = [self.nav_panel_image2, self.zoom_panel_image2]
        for panel in panels:
            panel.align_homography = np.identity(3)
            panel.corrected_img_shape = panel.raw_image.shape[:2]
            panel.update_all()
        
        self.sync_zooms_checkbox.Enable(True)
        self.sync_zooms_checkbox.SetValue(True)
    
    def on_align_right_to_left(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()
        
        if pts1 is None or pts2 is None:
            return
        
        if len(pts1) < 4:
            return
        
        H = cv2.findHomography(pts2.reshape(-1,1,2), 
                               pts1.reshape(-1,1,2))[0]
        self.nav_panel_image2.align_homography = H
        
        img_shape = self.nav_panel_image1.raw_image.shape[:2]
        panels = [self.nav_panel_image2, self.zoom_panel_image2]
        for panel in panels:
            panel.align_homography = H
            panel.corrected_img_shape = img_shape
            panel.update_all()
        
        panels = [self.nav_panel_image1, self.zoom_panel_image1]
        for panel in panels:
            panel.align_homography = np.identity(3)
            panel.corrected_img_shape = panel.raw_image.shape[:2]
            panel.update_all()
        
        self.sync_zooms_checkbox.Enable(True)
        self.sync_zooms_checkbox.SetValue(True)
    
    def on_load_image(self, event):
        fdlg = wx.FileDialog(self, 'Select an image.')
        if fdlg.ShowModal() == wx.ID_OK:
            file_path = fdlg.GetPath()
        else:
            return
        
        raw_image = cv2.imread(file_path)
        if raw_image.ndim == 3:
            # BGR to RGB.
            raw_image = raw_image[:,:,::-1]
        
        self.update_raw_image(raw_image)
            
    def on_save_image(self, event):
        fdlg = wx.FileDialog(self, 'Select an location to save the image.')
        if fdlg.ShowModal() == wx.ID_OK:
            file_path = fdlg.GetPath()
        else:
            return
        
        if self.raw_image.ndim == 3:
            cv2.imwrite(file_path, self.raw_image[:,:,::-1])
        else:
            cv2.imwrite(file_path, self.raw_image)
        
    def on_menu_item_about(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "Image Point Selection GUI"
        info.Version = "0.0.0"
        info.Copyright = "(C) 2017 Kitware"
        info.Description = wordwrap(
            "This GUI allows precise selection of image points",
            350, wx.ClientDC(self.navigation_panel))
        info.WebSite = ("http://www.kitware.com", "Kitware")
        info.Developers = ["Matt Brown"]
        info.License = wordwrap(license_str, 500, 
                                wx.ClientDC(self.navigation_panel))
        # Show the wx.AboutBox
        wx.AboutBox(info)
    
    def on_clear_last_button(self, event=None):
        for panel in [self.nav_panel_image1,
                      self.nav_panel_image2,
                      self.zoom_panel_image1,
                      self.zoom_panel_image2]:
            
            if self.click_state == 0:
                panel.clear_last_red_point(refresh=True)
            else:
                panel.clear_blue_points(refresh=True)
        
        self.click_state = 0
    
    def on_clear_all_button(self, event=None):
        for panel in [self.nav_panel_image1,
                      self.nav_panel_image2,
                      self.zoom_panel_image1,
                      self.zoom_panel_image2]:
            panel.clear_blue_points(refresh=False)
            panel.clear_red_points(refresh=True)
    
    def on_cancel_button(self, event=None):
        self.on_clear_all_button()
        self.Close()
        
    def on_finish_button(self, event=None):
        self.Close()
    
    def when_closed(self, event=None):
        if self.nav_panel_image1.red_points is not None and \
           self.nav_panel_image2.red_points is not None:
            points = np.hstack([self.nav_panel_image1.red_points,
                                self.nav_panel_image2.red_points])
        else:
            points = None
        
        self.passback_dict['points'] = points
        event.Skip()


def manual_registration(image1, image2, points=None, title1='Image 1', 
                        title2='Image 2'):
        """
        :param points: Initial points to use.
        :type points: Nx2 numpy.ndarray | None
        
        """
        passback_dict = {}
        if points is not None:
            assert points.shape[1] == 4
        
        passback_dict['points'] = points
        app = wx.App(True)
        frame = MainFrame(None, image1, image2, title1, title2, 
                          passback_dict=passback_dict)
        frame.Show(True)
        app.MainLoop()
        return passback_dict['points']


path = os.path.dirname(os.path.realpath(__file__))
def main():
    """
    :return: Pairs of clicked points.
    :rtype: None | Nx4 numpy.ndarray
    
    """
    path = os.path.dirname(os.path.realpath(__file__))
    fname = ''.join([path,'/../../../resources/test_image.png'])
    image1 = cv2.imread(fname)[:,:,::-1]
    theta = 10.0/180*np.pi
    h = np.array([[np.cos(theta),-np.sin(theta),0],
                  [np.sin(theta),np.cos(theta),0],
                  [0,0,1]])
    
    pts1 = np.random.rand(3, 20)
    pts1[0] *= image1.shape[1]
    pts1[1] *= image1.shape[0]
    pts1[2] = 1
    pts2 = np.dot(h, pts1);
    pts1 = (pts1[:2]/pts1[2]).T
    pts2 = (pts2[:2]/pts2[2]).T
    points = np.hstack([pts1, pts2])
    
    dsize = (1800,1600)
    image2 = cv2.warpPerspective(image1, h, dsize=dsize)
    pts = manual_registration(image1, image2, points)
    print('Returned', pts)
    return pts


if __name__ == '__main__':
    main()