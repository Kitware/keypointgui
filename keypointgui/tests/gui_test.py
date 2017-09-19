#!/usr/bin/env python
"""
ckwg +31
Copyright 2017 by Kitware, Inc.
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
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURcam_posE
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
from keypointgui.gui import manual_registration
import os
import cv2
import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
def main():
    """Generate test conditions.
    
    """
    fname = ''.join([path,'/image.jpg'])
    image1 = cv2.imread(fname)[:,:,::-1]
    theta = 30.0/180*np.pi
    h = np.array([[np.cos(theta),-np.sin(theta),0],
                  [np.sin(theta),np.cos(theta),0],
                  [0,0,1]])
    h[0,0] *= 1.5
    h[1,1] *= 2
    h[0,2] -= 500
    h[1,2] -= 1000
    
    pts1 = np.random.rand(3, 20)
    pts1[0] *= image1.shape[1]
    pts1[1] *= image1.shape[0]
    pts1[2] = 1
    pts2 = np.dot(h, pts1);
    pts1 = (pts1[:2]/pts1[2]).T
    pts2 = (pts2[:2]/pts2[2]).T
    points = np.hstack([pts1, pts2])
    
    dsize = (800,600)
    image2 = cv2.warpPerspective(image1, h, dsize=dsize)
    image2 =  cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    
    pts = manual_registration(image1, image2, points)
    print('Returned', pts)
    return pts


if __name__ == '__main__':
    main()