############################################
                 Keypoint GUI
############################################
.. image:: /docs/gui_demo_657x508.jpg
   :alt: gui_demo

Introduction
============
This project provides a GUI to select pairs of points between two images (see 
`image correspondence <https://en.wikipedia.org/wiki/Correspondence_problem>`_),
which can be saved or used to fit a homography. The GUI functionality is
implemented with wxPython 4.X with opencv-python image processing. Though, the 
tag `wxPython3X` provides compatibility with wxPython 3.X.

Project Layout
==============
The "source" code resides under the `keypointgui directory`:

- `gui.py` - the implementation of the GUI, which calls upon the layout defined in`form_builder_output.py`. This is the main "executable".

- `gui.fbp` - wxFormBuilder format file (`necessary version to edit GUI <https://ci.appveyor.com/api/projects/jhasse/wxformbuilder-461d5/artifacts/wxFormBuilder_win32.zip?branch=master>`_ or newer `repository here <www.wxformbuilder.org>`_).

- `form_builder_output.py` - automatically generated from `gui.fbp` using wxFormBuilder.

- `/tests/demo.py` - GUI demo.

Installation
============
1. Make sure Python is installed and visible from a command terminal:

.. code-block :: console

  $ python -V

2. Clone this repository into the desired directory:

.. code-block :: console

  $ git clone git@kwgitlab.kitware.com:matt.brown/keypointgui.git
  $ cd keypointgui

3. If wxPython 3.X is already on the system and you do not want to upgrade to 4.x:

.. code-block :: console

  # Check if wxPython 3.X is already installed (print version)
  $ python -c "import wx;print wx.__version__"
  
  # If version 3.X is present, checkout the wxPython3X branch:
  $ git checkout wxPython3X
 
4. If using Ubuntu 16.04 (otherwise pip will try to build from source and fail):

.. code-block :: console
  
  $ sudo pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 wxPython

5. Install with all dependencies (OpenCV and wxPython):

.. code-block :: console

  $ pip install .

This package can be uninstalled by:

.. code-block :: console

  $ pip uninstall keypointgui

Usage Instructions
==================

You can launch the GUI with:

.. code-block :: console

  $ python -m keypointgui.gui

The GUI is initially empty, but you can load your images using the menu options:

  File -> Load Left Image

  File -> Load Right Image

The top two panes are global views of the loaded images, and the red rectangles
indicate the regions shown magnified in the associated bottom panes. Clicking in
either upper pane will recenter the zoomed region, and the mousewheel controls
the magnification. Clicking in either of the lower images will create a
temporary blue point. The same feature should be clicked in the other lower
image, and then both points will turn red, establishing an image point
correspondence. This process is repeated to build up a set of image point
correspondences between the two images.

Image Alignment
---------------

If the two source images differ in scale or orientation, the task of selecting
points can be challenging. After at least four pairs of points have been
selected, an alignment homography can be fitted to the points using the
`Left-->Right` or `Right-->Left` buttons. To get an accurate alignment, these
initial four points should be selected from the four corners of the image or
spread out as much as possible. In the aligned state, point selection can
proceed in the same manner as previously detailed, and the selected points are
automatically transformed back to the full-resolution, source-image coordinate
system when saving points or generating a homography.

In the aligned state, the `Sync Zooms` options defaults to checked. With this
feature enabled, clicking on either top panel will recenter the zoom regions for
both images onto roughly the same feature.

Saving Points
-------------

The menu option:

  File -> Save Points

will save a text file of the currently selected points. In this file, each row
represents one pair of points, with the first two columns representing the (x,y)
coordinates of the point in the left image and the last two columns representing
the (x,y) coordinates of the point in the right image. The convention for image
coordinates is such that the center of the top left pixel has coordinates (0,0).

Saving Homography
-----------------

The menu options:

  File -> Save Left->Right Homography

  File -> Save Right->Left Homography

saves a homography to a text file that warps coordinates from the left image
into the right image or the right image into the left image, respectively.

