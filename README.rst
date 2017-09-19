This project provides a GUI enabling the user to select pairs of points between
images (see `image correspondence <https://en.wikipedia.org/wiki/Correspondence_problem>`_)
and fits a homography to the correspondence. The GUI functionality is
implemented with wxPython.

The "source" code resides under the `keypoint_matching_gui directory`.
`wx_elements.py` - provides generic wxPython functionality
`gui.py` - the implementation of the GUI, which calls upon the layout defined in
`form_builder_output.py`.
`gui.fbp` - wxFormBuilder format file (`necessary version <https://sourceforge.net/projects/wxformbuilder/files/wxformbuilder-nightly/3.4.2-beta/>`_.
`form_builder_output.py` - automatically generated from `gui.fbp` using
wxFormBuilder.
