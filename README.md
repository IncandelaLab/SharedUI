# SharedUI

------

## Prerequisites

This GUI requires Python 3.  It's been tested thoroughly with Python 3.7 and less thoroughly with Python 3.6; versions 3.4 and earlier are incompatible with PyQt5.

Two packages are required:  numpy and PyQt5.  Previous versions of the GUI used PyQt4 instead, but the code is no longer compatible with it.  Installation instructions for PyQt5 can be found [here.](https://doc.bccnsoft.com/docs/PyQt5/installation.html)

It's recommended to use Qt Creator for editing the .ui files.  If it's not already installed, you can download it from the Qt Creator tab of [this page.](https://www.qt.io/offline-installers)  After making changes to the .ui files, run the script `compile.sh` (or `compile.bat`) in the .ui files' directory to carry all of the changes over to the corresponding .py files.  (Note:  Adding new .ui files will require you to modify compile.sh and compile.bat accordingly.)

## Running and using the GUI

Running the GUI is straightforward:  Run `python mainUI.py` in a terminal to launch it.  On Windows, you can run the batch file `run.bat` instead through either the terminal or the file manager.

The GUI is divided into three sections:  Parts, tooling, and supplies; production steps and testing routines; and shipping.  In each section, you can enter in data by choosing the object ID number and clicking 'new' (or 'edit' if the object already has data).  A few pages, such as the kapton placement step, will display errors in a status box if there's a problem with the input, preventing the input from being saved until all problems are resolved.  For now, all data provided to the GUI is saved locally in .json files:  The GUI will create a new directory `filemanager_data` in the parent directory of SharedUI and store the files accordingly.

Currently, .ui pages for the Unbiased DAQ and IV Curve pages exist but are not yet integrated into the GUI.
