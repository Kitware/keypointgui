#!/usr/bin/env python
from __future__ import division, print_function
import wx
from wx.lib.wordwrap import wordwrap
import form_builder_output
import cv2
import numpy as np
import os

license_str = ''.join(['Copyright 2017-2018 by Kitware, Inc.\n',
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


class ImagePanelManager(object):
    """Base class for an image contained within a panel.

    This class allows a warped version of an image to be displayed in a panel
    while providing convenient operations defined in raw image coordinates.
    This object contains a raw version of an image but displays a warped
    version in the panel defined by a homography. When a user clicks on the
    panel image, the abstract method 'process_clicked_point' is called with the
    raw-image coordinates of the feature that was clicked. Likewise, if an
    instance of wx.StatusBar is passed, the raw-image coordinates will be
    displayed when the mouse hovers over the image.

    The object also allows blue and red circle markers to be specified in
    raw-image coordinates and then appropriately drawn on the warped image in
    the panel.

    Common subclass functionality include rescaling an image to fit the panel
    and warping the image to rectify it relative to another panel image.

    Note: the image coordinate system has its orgin (0,0) at the center of the
    upper left pixel.

    Attributes:
    :param raw_image: The original full-resolution source image.
    :type raw_image: numpy.ndarray

    :param wx_panel: Panel to add the image to.
    :type wx_panel: wx.Panel

    :param homography: Homography that warps from the raw_image coordinate
        system to the panel image coordinate system.
    :type homography: numpy.ndarray of shape (3,3)

    :param wx_image: Image container with size matching the wx_panel size.
    :type wx_image: wx.Image

    :param wx_bitmap: Image container with size matching the wx_panel size.
    :type wx_bitmap: wx.Bitmap

    :param blue_points: Raw image coordinates to draw blue circles at.
    :type blue_points: Nx2 numpy.ndarray

    :param red_points: Raw image coordinates to draw red circles at.
    :type red_points: Nx2 numpy.ndarray

    """
    def __init__(self, wx_panel, raw_image=None, interpolation=1,
                 status_bar=None, blue_points=None, red_points=None):
        """Abstract base class.

        :param wx_panel: Panel to add the image to.
        :type wx_panel: wx.Panel

        :param image: Image.
        :type raw_image: numpy.ndarray | None

        :param interp: Integer specifying the quality of the interpolation. The
            values ranges for 0-4 and corresponds to nearest neighbor, linear,
            area, cubic, and lanczos4 respectively.
        :type interp: None | int

        :param status_bar: Status bar.
        :type status_bar: wx.StatusBar | None

        :param blue_points: Raw image coordinates to draw blue circles at.
        :type blue_points: Nx2 numpy.ndarray

        :param red_points: Raw image coordinates to draw red circles at.
        :type red_points: Nx2 numpy.ndarray

        """
        self.wx_panel = wx_panel
        self.raw_image = raw_image
        self.image = None
        self.wx_image = None
        self.blue_points = blue_points
        self.red_points = red_points
        self.circle_radius = 5
        self.circle_thickness = 3

        if interpolation is not None:
            self.set_interpolation(interpolation)

        self.status_bar = status_bar

        # Needed by
        self.wx_panel.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # ------------------------ Bind Events -------------------------------
        # The image coordinates are aligned with the panel coordinates, so we
        # can listen for panel clicks and use the panel coordinate as the image
        # coordinates.
        self.wx_panel.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.wx_panel.Bind(wx.EVT_RIGHT_DOWN, self.on_click)
        self.wx_panel.Bind(wx.EVT_MOTION, self.on_mouse_over)

        self.wx_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.wx_panel.Bind(wx.EVT_SIZE, self.on_size)
        # --------------------------------------------------------------------

    def update_raw_image(self, raw_image):
        """Replace raw_image and update the rendered view in the panel.

        """
        self.raw_image = raw_image
        #self.update_all()

    def warp_image(self):
        """Apply homography.

        """
        if self.raw_image is not None and self.inverse_homography is not None:
            panel_width, panel_height = self.wx_panel.GetSize()
            flags = self.interpolation | cv2.WARP_INVERSE_MAP
            image = cv2.warpPerspective(self.raw_image,
                                        self.inverse_homography,
                                        dsize=(panel_width, panel_height),
                                        flags=flags)

            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            self.wx_image.SetData(image.tostring())
            self.wx_bitmap = self.wx_image.ConvertToBitmap()

    def on_click(self, event):
        """Called on events wx.EVT_RIGHT_DOWN or wx.EVT_LEFT_DOWN.

        """
        if self.raw_image is not None:
            pos = event.GetPosition()
            pos = np.dot(self.inverse_homography, [pos[0],pos[1],1])
            pos = pos[:2]/pos[2]

            if event.LeftDown():
                button = 0
            elif event.RightDown():
                button = 1
            else:
                button = None

            self.process_clicked_point(pos, button)

    def on_mouse_over(self, event):
        """Called on event wx.EVT_MOTION.

        """
        if self.status_bar is not None and self.raw_image is not None:
            pos = event.GetPosition()
            pos = np.dot(self.inverse_homography, [pos[0],pos[1],1])
            pos = pos[:2]/pos[2]
            if np.all([pos[0] >= 0,
                       pos[0] <= self.raw_image.shape[1],
                       pos[0] >= 0,
                       pos[1] <= self.raw_image.shape[0]]):

                pos = tuple(pos)
                # If coordinates are actually within the image.
                disp_str = 'Raw Image Coordinates ({:.2f},{:.2f})'.format(*pos)
                self.status_bar.SetStatusText(disp_str)
            else:
                self.status_bar.SetStatusText('')

    def set_interpolation(self, interp):
        """
        :param interp: Integer specifying the quality of the interpolation. The
            values ranges for 0-4 and corresponds to nearest, linear, area,
            cubic, and lanczos4 respectively.
        :type interp: None | int
        """
        if interp == 0:
            self.interpolation = cv2.INTER_NEAREST
        elif interp == 1:
            self.interpolation = cv2.INTER_LINEAR
        elif interp == 2:
            self.interpolation = cv2.INTER_AREA
        elif interp == 3:
            self.interpolation = cv2.INTER_CUBIC
        elif interp == 4:
            self.interpolation = cv2.INTER_LANCZOS4
        else:
            raise Exception('Invalid value for interp: {}'.format(interp))

    def on_size(self, event):
        """Called on event wx.EVT_SIZE.

        """
        self.update_all()

    def update_all(self):
        if self.raw_image is not None:
            #print('on_size')
            panel_width, panel_height = self.wx_panel.GetSize()
            self.wx_image = wx.EmptyImage(panel_width, panel_height)
            self.update_homography()
            self.update_inverse_homography()
            self.warp_image()
            self.wx_panel.Refresh(True)

    # ----------------- Manage Points that will be Displayed -----------------
    def set_blue_points(self, points, refresh=True):
        points = np.atleast_2d(np.array(points, dtype=np.float64))
        self.blue_points = points

        if refresh:
            self.wx_panel.Refresh(True)

    def add_blue_point(self, point, refresh=True):
        """
        :param point:
        :type point: numpy.ndarray

        """
        #point = np.atleast_2d(point.ravel()).T
        point = np.atleast_2d(point)
        if self.blue_points is None:
            self.set_blue_points(point, refresh)
        else:
            self.set_blue_points(np.vstack([self.get_blue_points(), point]),
                                 refresh)

    def get_blue_points(self):
        return self.blue_points

    def set_red_points(self, points, refresh=True):
        points = np.atleast_2d(np.array(points, dtype=np.float64))
        self.red_points = points

        if refresh:
            self.wx_panel.Refresh(True)

    def add_red_point(self, point, refresh=True):
        """
        :param point:
        :type point: numpy.ndarray

        """
        #point = np.atleast_2d(point.ravel()).T
        point = np.atleast_2d(point)
        if self.red_points is None:
            self.set_red_points(point, refresh)
        else:
            self.set_red_points(np.vstack([self.get_red_points(), point]),
                                refresh)

    def get_red_points(self, refresh=True):
        return self.red_points

    def clear_last_blue_point(self, refresh=True):
        if self.blue_points is not None:
            if len(self.blue_points) == 1:
                self.blue_points = None
            else:
                self.blue_points = self.blue_points[:-1]
        if refresh:
            self.wx_panel.Refresh(True)

    def clear_last_red_point(self, refresh=True):
        if self.red_points is not None:
            if len(self.red_points) == 1:
                self.red_points = None
            else:
                self.red_points = self.red_points[:-1]
        if refresh:
            self.wx_panel.Refresh(True)

    def clear_blue_points(self, refresh=True):
        self.blue_points = None
        if refresh:
            self.wx_panel.Refresh(True)

    def clear_red_points(self, refresh=True):
        self.red_points = None
        if refresh:
            self.wx_panel.Refresh(True)
    # -----------------------------------------------------------------------

    def on_paint(self, event=None):
        """Called on event wx.EVT_PAINT.

        """
        #print('on_paint', self)
        if self.wx_image is not None:
            # AutoBufferedPaintDC helps avoid flicker.
            #dc = wx.AutoBufferedPaintDC(self.wx_panel)
            dc = wx.PaintDC(self.wx_panel)
            #dc = wx.BufferedDC(dc)
            dc.DrawBitmap(self.wx_bitmap, 0,0)
            self.draw_overlay(dc)

        if self.blue_points is not None:
            dc.SetPen(wx.Pen(wx.BLUE, self.circle_thickness))
            dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT))
            for i in range(len(self.blue_points)):
                x, y = self.blue_points[i]
                pt = np.dot(self.homography, [x,y,1])
                x, y = pt[:2]/pt[2]
                dc.DrawCircle(x, y, self.circle_radius)

        if self.red_points is not None:
            dc.SetPen(wx.Pen(wx.RED, self.circle_thickness))
            dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT))
            for i in range(len(self.red_points)):
                x, y = self.red_points[i]
                pt = np.dot(self.homography, [x,y,1])
                x, y = pt[:2]/pt[2]
                dc.DrawCircle(x, y, self.circle_radius)

        if event is not None:
            event.Skip()

    def refresh(self, event):
        """Useful to bind the Refresh of self.wx_panel to an event.

        """
        event.Skip()
        self.wx_panel.Refresh(True)

    def draw_overlay(self, dc):
        pass

    def update_inverse_homography(self):
        """
        Calculate inverse of the homography.

        """
        if self.homography is None:
            return None
        else:
            self.inverse_homography = np.linalg.inv(self.homography)

    def update_homography(self):
        """
        Determine what the homography should be based on all existing
        attributes.

        """
        return np.identity(3)

    def process_clicked_point(self, pos, button):
        """
        :param pos: Raw image coordinates that were clicked.
        :type pos: 2-array

        :param button: The mouse button that was clicked (0 for left, 1 for
            right)
        :type button: 0 | 1

        """
        pass


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
        super(NavigationPanelImage, self).__init__(wx_panel, image,
             status_bar=status_bar)
        self.zoom_panel_image = zoom_panel_image
        self.align_homography = np.identity(3)

        if self.raw_image is not None:
            self.corrected_img_shape = self.raw_image.shape[:2]

        # When the zoom panel changes, make sure the navigation panel is
        # redrawn.
        self.zoom_panel_image.wx_panel.Bind(wx.EVT_PAINT, self.refresh)

    def update_raw_image(self, raw_image):
        if raw_image is None:
            return False

        super(NavigationPanelImage, self).update_raw_image(raw_image)
        self.corrected_img_shape = self.raw_image.shape[:2]
        self.zoom_panel_image.update_raw_image(raw_image)

    def update_homography(self):
        #print('on_size')
        panel_width, panel_height = self.wx_panel.GetSize()

        if False:
            im_height, im_width = self.raw_image.shape[:2]
            print('Panel Size ({}, {})'.format(panel_width, panel_height))
            print('Original Image Size ({}, {})'.format(im_width, im_height))

        # The corrected image shape comes from the dimensions of the image that
        # this one is being corrected to.
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
    def __init__(self, wx_panel, image=None, zoom=400, center=None,
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
        super(ZoomPanelImage, self).__init__(wx_panel, image,
             status_bar=status_bar)

        if center is None and self.raw_image is not None:
            self._center = np.array(self.raw_image.shape[:2][::-1])/2

        self.align_homography = np.identity(3)

        if self.raw_image is not None:
            self.corrected_img_shape = self.raw_image.shape[:2]

        self.zoom_spin_button = zoom_spin_button
        self.zoom_label = zoom_label

        self.click_callback = click_callback

        self.handle_updated_zoom(zoom)

        self.zoom_spin_button.Bind(wx.EVT_SPIN_DOWN, self.on_zoom_down)
        self.zoom_spin_button.Bind(wx.EVT_SPIN_UP, self.on_zoom_up)
        self.wx_panel.Bind(wx.EVT_MOUSEWHEEL, self.on_zoom_mouse_wheel)

    @property
    def zoom(self):
        return self._zoom

    def update_raw_image(self, raw_image):
        if raw_image is None:
            return False

        super(ZoomPanelImage, self).update_raw_image(raw_image)
        self.corrected_img_shape = self.raw_image.shape[:2]
        self._center = np.array(self.raw_image.shape[:2][::-1])/2

    def set_zoom(self, zoom):
        """
        :param zoom: Zoom percentage.
        :type zoom: float
        """
        self._zoom = zoom
        self.zoom_label.SetLabel('{}%'.format(int(np.round(zoom))))
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
    def __init__(self, parent, image1, image2, title1='Let Image',
                 title2='Right Image', passback_dict={'points',None},
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

        # Allow zooming by mouse scrolling from the upper navigation panels.
        self.image1_nav_panel.Bind(wx.EVT_MOUSEWHEEL,
                                   self.zoom_panel_image1.on_zoom_mouse_wheel)
        self.image2_nav_panel.Bind(wx.EVT_MOUSEWHEEL,
                                   self.zoom_panel_image2.on_zoom_mouse_wheel)

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
        Clicked on point in image 1 (left image).

        :param pos: Raw image coordinates of the clicked point.

        """
        if button == 1:
            self.zoom_panel_image1.set_center(pos)
            if self.sync_zooms_checkbox.GetValue():
                h1 = self.nav_panel_image1.align_homography
                h2 = self.nav_panel_image2.align_homography
                h = np.dot(np.linalg.inv(h2), h1)
                pos2 = np.dot(h, np.hstack([pos,1]))
                self.zoom_panel_image2.set_center(pos2[:2]/pos2[2])

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
        Clicked on point in image 2 (right image).

        :param pos: Raw image coordinates of the clicked point.

        """
        if button == 1:
            self.zoom_panel_image2.set_center(pos)
            if self.sync_zooms_checkbox.GetValue():
                h1 = self.nav_panel_image1.align_homography
                h2 = self.nav_panel_image2.align_homography
                h = np.dot(np.linalg.inv(h1), h2)
                pos2 = np.dot(h, np.hstack([pos,1]))
                self.zoom_panel_image1.set_center(pos2[:2]/pos2[2])

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
            if panel.raw_image is not None:
                panel.corrected_img_shape = panel.raw_image.shape[:2]
                panel.update_all()

        self.sync_zooms_checkbox.SetValue(False)
        self.sync_zooms_checkbox.Enable(False)

    def on_align_left_to_right(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()
        if pts1 is None or pts2 is None or len(pts1) < 4:
            msg = 'Need at least four selected pairs of points to align images.'
            dlg = wx.MessageDialog(self, msg,'Warning',
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        H = cv2.findHomography(pts1.reshape(-1,1,2),
                               pts2.reshape(-1,1,2))[0]
        self.nav_panel_image1.align_homography = H

        # Set zooms so that they match after alignment.
        self.zoom_panel_image1.set_zoom(self.zoom_panel_image2.zoom)

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

        if pts1 is None or pts2 is None or len(pts1) < 4:
            msg = 'Need at least four selected pairs of points to align images.'
            dlg = wx.MessageDialog(self, msg,'Warning',
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        H = cv2.findHomography(pts2.reshape(-1,1,2),
                               pts1.reshape(-1,1,2))[0]
        self.nav_panel_image2.align_homography = H

        # Set zooms so that they match after alignment.
        self.zoom_panel_image2.set_zoom(self.zoom_panel_image1.zoom)

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

    def on_load_left_image(self, event):
        self.load_image(self.nav_panel_image1)

    def on_load_right_image(self, event):
        self.load_image(self.nav_panel_image2)

    def load_image(self, panel):
        fdlg = wx.FileDialog(self, 'Select an image.')
        if fdlg.ShowModal() == wx.ID_OK:
            file_path = fdlg.GetPath()
        else:
            return

        raw_image = cv2.imread(file_path)

        if raw_image is None:
            print("Cannot open image.")
            return False

        if raw_image.ndim == 3:
            # BGR to RGB.
            raw_image = raw_image[:,:,::-1]

        panel.update_raw_image(raw_image)

        self.on_align_original(None)

    def on_save_points(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()

        if pts1 is None or pts2 is None:
            msg = 'No points have been selected.'
            dlg = wx.MessageDialog(self, msg,'Warning',
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        fdlg = wx.FileDialog(self, 'Save point correspondences', os.getcwd(),
                             'points', '*.txt', wx.SAVE|wx.OVERWRITE_PROMPT)
        if fdlg.ShowModal() == wx.ID_OK:
            file_path = fdlg.GetPath()
        else:
            return

        points = np.hstack([pts1,pts2])
        np.savetxt(file_path, points)

    def on_save_left_to_right_homography(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()
        self.save_homography(pts1, pts2)

    def on_save_right_to_left_homography(self, event):
        pts1 = self.nav_panel_image1.get_red_points()
        pts2 = self.nav_panel_image2.get_red_points()
        self.save_homography(pts2, pts1)

    def save_homography(self, pts1, pts2):
        if pts1 is None or pts2 is None or len(pts1) < 4:
            msg = ''.join(['Need at least four selected pairs of points to ',
                           'calculate homography.'])
            dlg = wx.MessageDialog(self, msg,'Warning',
                                   wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        fdlg = wx.FileDialog(self, 'Save homography',
                             os.getcwd(), 'homography', '*.txt',
                             wx.SAVE|wx.OVERWRITE_PROMPT)
        if fdlg.ShowModal() == wx.ID_OK:
            file_path = fdlg.GetPath()
        else:
            return

        H = cv2.findHomography(pts1.reshape(-1,1,2),
                               pts2.reshape(-1,1,2))[0]
        np.savetxt(file_path, H)

    def on_menu_item_about(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "Image Point Selection GUI"
        info.Version = "0.0.0"
        info.Copyright = "(C) 2017 Kitware"
        info.Description = wordwrap(
            "This GUI allows precise selection of image points",
            350, wx.ClientDC(self))
        info.WebSite = ("http://www.kitware.com", "Kitware")
        info.Developers = ["Matt Brown"]
        info.License = wordwrap(license_str, 500,
                                wx.ClientDC(self))
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


def manual_registration(image1=None, image2=None, points=None,
                        title1='Left Image', title2='Right Image'):
        """Launch manual key point registration GUI.

        :param image1: Left image.
        :type image1: numpy.ndarray

        :param image2: Right image.
        :type image2: numpy.ndarray

        :param points: Initial points to use.
        :type points: Nx2 numpy.ndarray | None

        :return: Selecterd points.
        :rtype: Nx2 numpy.ndarray

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


def main():
    """

    """
    pts = manual_registration(None, None)


if __name__ == '__main__':
    main()