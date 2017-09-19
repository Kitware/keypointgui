Introduction
============

This project provides a GUI enabling the user to select pairs of points between
images (see `image correspondence <https://en.wikipedia.org/wiki/Correspondence_problem>`_),
which can be saved or used to fit a homography. The GUI functionality is
implemented with wxPython.

Project Layout
==============
The "source" code resides under the `keypointgui directory`:

- `gui.py` - the implementation of the GUI, which calls upon the layout defined in`form_builder_output.py`. This is the main "executable".

- `gui.fbp` - wxFormBuilder format file (`necessary version to edit GUI <https://sourceforge.net/projects/wxformbuilder/files/wxformbuilder-nightly/3.5.1-rc1/>`_).

- `form_builder_output.py` - automatically generated from `gui.fbp` using wxFormBuilder.

- `/tests/gui_test.py` - test of the GUI showing programmatic launching of the GUI from within Python.

Instructions
============

You can launch the GUI from within the top-level project directory with the
following call:

  $ python keypointgui/gui.py

The GUI is initially empty, but you can load your images using the menu options:

  File -> Load Left Image

  File -> Load Right Image

The top two panes are global views of the loaded images. Clicking in either
upper pane will set the zoom location shown in the lower pane. Clicking in
either of the lower images will create a temporary blue point. The same feature
should be clicked in the other lower image, and then both points will turn red,
establishing an image point correspondence. This process is repeated to build up
a set of image point correspondences between the two images.

Image Alignment
---------------

If the two source images differ in scale or orientation, the task of selecting
points can be challenging. After at least four pairs of points have been
selected, an initial alignment can be generate using the `Left-->Right` or
`Right-->Left` buttons. To get an accurate alignment, these initial four points
should be selected from the four corners of the image or spread out as much as
possible. In the aligned state, point selection can proceed in the same manner
as previously detailed, and the selected points are automatically transformed
back to the source image coordinate system when saving points or generating a
homography.

In the aligned state, the `Sync Zooms` options defaults to checked. With this
feature enabled, clicking on either top panel will zoom both lower panels to
roughly the same feature.

Saving Points
-------------

The menu option:

  File -> Save Points

will save a text file of the currently selected points. In this file, each row
represents one pair of points, with the first two columns representing the (x,y)
coordinates of the point in the left image and the last two columns representing
the (x,y) coordinates of the point in the right image. The convention for image
coordinates is such that the center of the topic left pixel has coordinates
(0,0).

Saving Homography
-----------------

The menu options:

  File -> Save Left->Right Homography

  File -> Save Right->Left Homography

saves a homography to a text file that warps coordinates from the left image 
into the right image or the right image into the left image, respectively.
