#!/usr/bin/env python
"""
ckwg +31
Copyright 2016-2017 by Kitware, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

 * Neither name of Kitware, Inc. nor the names of any contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==============================================================================

"""
from __future__ import division, print_function
import wx
import cv2
import numpy as np
#from abc import ABCMeta, abstractmethod

import rospy
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError

from PIL import Image as PILImage
import StringIO
 
class SimpleImagePanelManager(object):
    def __init__(self, wx_panel, raw_image=None, interpolation=1, **kwargs):
        self.wx_panel = wx_panel
        self.raw_image = raw_image
        # The following three images are either all None or all forms of the same image.
        self.image = None
        self.wx_image = None
        self.wx_bitmap = None

        if interpolation is not None:
            self.set_interpolation(interpolation)

        self.wx_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.wx_panel.Bind(wx.EVT_SIZE, self.on_size)

    def update_raw_image(self, raw_image):
        """Replace raw_image and update the rendered view in the panel.
        
        """
        self.raw_image = raw_image
        self.update_all()

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
            self.update_wx_bitmap()
            self.wx_panel.Refresh(True)

    def fit_image_in_panel(self,width,height):
        iheight,iwidth,depth = self.raw_image.shape
        iratio = float(iwidth)/float(iheight)
        ratio = float(width)/float(height)
        if iratio > ratio:
            ret = (width,min(int(width/iratio),height))
        else:
            ret = (min(int(height*iratio),width),height)
        return ret

    def update_wx_bitmap(self):
        panel_width, panel_height = self.wx_panel.GetSize()
        dims = self.fit_image_in_panel(panel_width, panel_height)
        self.wx_image = wx.EmptyImage(dims[0],dims[1])
        self.image = cv2.resize(self.raw_image, dims,
                                interpolation=self.interpolation)
        self.wx_image.SetData(self.image.tostring())
        self.wx_bitmap = self.wx_image.ConvertToBitmap()

    def on_paint(self, event=None):
        """Called on event wx.EVT_PAINT.
        
        """
        #print('on_paint', self)
        if self.wx_bitmap is not None:
            # AutoBufferedPaintDC helps avoid flicker.
            #dc = wx.AutoBufferedPaintDC(self.wx_panel)
            dc = wx.PaintDC(self.wx_panel)
            #dc = wx.BufferedDC(dc)
            dc.DrawBitmap(self.wx_bitmap, 0,0)
            self.draw_overlay(dc)

        if event is not None:
            event.Skip()

    def clear(self):
        self.raw_image = None
        self.image = None
        self.wx_image = None
        self.wx_bitmap = None
        self.wx_panel.Refresh()

    def draw_overlay(self, dc):
        pass

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
    #__metaclass__ = ABCMeta
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
        self.update_all()
    
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

class ROSTopicImagePanelManager(SimpleImagePanelManager):
    # Instantiate a CvBridge as a class variable
    bridge = CvBridge()

    def __init__(self, wx_panel, image_topic=None, **kwargs):
        super(ROSTopicImagePanelManager, self).__init__(wx_panel, **kwargs)

        self.image_subscriber = None

        self.image_topic = None
        self.update_image_topic(image_topic)

        self.image_update_handled = True

        wx_panel.Bind(wx.EVT_IDLE, self.handle_new_raw_image)

    def is_compressed_topic( self, topic ):
        return topic.split( '/' )[-1] == 'compressed'

    def update_image_topic(self, new_image_topic):
        if self.image_topic == new_image_topic:
            return
        if self.image_subscriber is not None:
            self.image_subscriber.unregister()

        self.image_topic = new_image_topic
        if self.image_topic is not None:
            msg_type = Image
            callback = self.update_image_ros
            if self.is_compressed_topic( self.image_topic ):
                msg_type = CompressedImage
                callback = self.update_compressed_image_ros
            self.image_subscriber = rospy.Subscriber( self.image_topic, msg_type,
                                                      callback )
        else:
            self.image_subscriber = None
            self.clear()

    def update_image_ros(self, msg):
        """
        :param msg: Image message.
        :type msg: sensor_msgs.msg.Image
        
        """
        wx.CallAfter(self.update_image, msg, False)

    def update_compressed_image_ros( self, msg ):
        wx.CallAfter(self.update_image, msg, True)

    def update_image( self, image_msg, is_compressed ):
        if self.image_subscriber is not None:
            self.image_msg = image_msg
            self.is_compressed = is_compressed
            self.image_update_handled = False

    def handle_new_raw_image(self, event):
        if not self.image_update_handled:
            self.image_update_handled = True

            if self.is_compressed:
                sio = StringIO.StringIO( self.image_msg.data )
                im = PILImage.open( sio )
                image = np.array( im )
                image = image[:, :, ::-1].copy()
            else:
                try:
                    # Convert your ROS Image message to OpenCV2
                    image = ROSTopicImagePanelManager.bridge.imgmsg_to_cv2(self.image_msg, "bgr8")
                except CvBridgeError, e:
                    print(e)
                    return

            if image.ndim == 3:
                # BGR to RGB
                image = image[...,::-1]

            self.update_raw_image(image)

    def close(self):
        if self.image_subscriber is not None:
            self.image_subscriber.unregister()
            self.image_subscriber = None
