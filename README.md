# SharedUI

------

NOTE:  This is a beta version of the module assembly GUI.  Pages for the module assembly steps and wirebonding are currently disabled, as the database has not been set up to handle them yet.  Please let me know if you have any questions or run into any bugs--my email is pmasterson@ucsb.edu, and I should usually be able to respond within a day.

## Prerequisites

This GUI requires Python 3.  It's been tested thoroughly with Python 3.7 and less thoroughly with Python 3.6; versions 3.4 and earlier are incompatible with PyQt5.

Currently, the GUI is designed to run on a Mac machine, and may run into issues on other operating systems.  To install the GUI, simply download and clone the git repository, then run the script `install_dependencies.sh` with the following command:

```
bash install_dependencies.sh path/to/software//dir
```

The script will install all software prerequisites in `path/to/software/dir`; this can be any location.  The installation script should work on linux as well, but has not been tested thoroughly, and will not work on Windows at present.

Additionally, all users will need a lxplus account.  You will need to add yourself to the cms-hgcal-assemblyOperators [E-group](https://e-groups.cern.ch/e-groups/EgroupsSearchForm.do) in order to get permission to upload to the DB.

**For developers only:**  It's recommended to use Qt Creator for editing the .ui files.  If it's not already installed, you can download it from the Qt Creator tab of [this page.](https://www.qt.io/offline-installers)  After making changes to the .ui files, run the script `compile.sh` (or `compile.bat`) in the .ui files' directory to carry all of the changes over to the corresponding .py files.  (Note:  Adding new .ui files will require you to modify compile.sh and compile.bat accordingly.)  Installing SQL Developer is also highly recommended for developers, since you may need to view the raw contents of the DB and test SQL queries.  You can download it [here.](https://www.oracle.com/database/sqldeveloper/technologies/download/)

## Running and using the GUI

To run the GUI, `cd` into the `SharedUI` directory and use the following command:

```
python mainUI.py
```

A dialog box asking for your lxplus username will pop up.  After inputting your lxplus username and password, the main GUI window should open up immediately.

The GUI is divided into two main sections:  Parts, tooling, and supplies; and production steps and testing routines.  There is also a part search page that lets users quickly find parts that have been uploaded to the DB.  To switch between pages, simply double-click on the page name in the sidebar.  (If a page does not open, it's probably WIP.)

### Parts, tooling, and supplies

Before performing a production step, all necessary parts, tools, and supplies must be created using their respective pages.  For instance, a kapton placement step requires an existing sensor tool, baseplate, sensor component tray, etc.  To create a part, enter the desired part ID into the "[part] ID" box on the corresponding page, then click "New".  You can then save the changes with "Save" or discard them with "Cancel".  "Load" will check the DB to see whether a part exists, and if the part is found, all relevant data will be downloaded so you can view and edit it.  Parts may also be edited after creation with the "Edit" button (if it's greyed-out, try pressing "Load" first).

Once a part has been created and saved, it can be uploaded to the DB with the "Upload current object" in the sidebar.  **You will then need to switch to the terminal window that you used to open the GUI and enter in your lxplus password twice**--once for the XML file that creates the part, and 20 seconds later, once for the XML file that uploads measurement data.  (This is a bit of a kludge, and I'm currently looking into ways to upload the files without asking for a password every time.)

Note that protomodules and modules are automatically created by the sensor placement and pcb placement steps, respectively.  They cannot be created manually, but can be edited after creation.  (Some protomodule/module information can't be inherited from their component parts, and has to be entered in manually.)

In the future, all baseplates, sensors, and PCBs should be entered into the DB prior to being shipped to MACs, and creation of those parts with the GUI will be disabled.

### Production steps and testing routines

WIP - not currently implemented

Once all necessary information in the parts, tooling, and supplies section has been filled in, you can proceed to the production steps.  The production step pages are broadly similar to the previous ones, but with one major difference:  the data will be automatically checked for errors, and if any are found, a message will appear in the status box.  Once all errors have been resolved, you can save the step.

### Part search

To use the part search page, simply select the type of part you want to search for using the drop-down menu at the upper-left-hand corner, then select any other criteria you want using the options below.  You can then press "Search" to perform the query and display the results.  Lastly, you can jump to a part's info page by clicking on the part name in the "search results" box, then clicking the "Go to selected item" button underneath.


