# SharedUI

------

SharedUI is a graphical user interface designed help engineers monitor and record data during the module assembly process.  Currently, the final product of the GUI is a number of XML files formatted for the HGCAL DB loader.  In the future, it will be possible to automatically store recorded data in the central DB, as well as retrive data for completed parts or assembly steps.

**NOTE:**  This is a beta version of the module assembly GUI.  **Uploading to the DB has not been implemented yet, and all data will be saved locally.**  Please let me know at pmasterson@ucsb.edu if you have any questions or run into any bugs--I should usually be able to respond within a day.

## Prerequisites

This GUI requires Python 3.  It's been tested thoroughly with Python 3.7+ and less thoroughly with Python 3.6; versions 3.4 and earlier are incompatible with PyQt5.

Additionally, the GUI has been deveoped on a Mac machine, and may run into issues on other operating systems.  (Update:  The GUI appears to work fine on Windows, but has not been extensively tested yet.)

To install the GUI, simply download and clone the git repository:

```
git clone https://github.com/p-masterson/SharedUI.git
```

Next, install the required python packages with:

```
python -m pip install numpy PyQt5 jinja2 pytest
```

An installation script `install_dependencies.sh` may be required in the future for installing software required for DB communication, but it is currently WIP and should not be used.

## Running and using the GUI

To run the GUI, `cd` into the `SharedUI` directory and run the following command:

```
python mainUI.py
```

If your default python version is 2.x, you may need to use `python3 mainUI.py` instead.

The GUI is divided into two main sections:  Parts, tooling, and supplies; and production steps and testing.  There is also a part search page that lets users quickly find existing parts.  To switch between pages, simply double-click on the page name in the sidebar.  (If a page does not open, it's probably WIP.)

### Parts, tooling, and supplies

Before performing an assembly step, you will have to go through the parts, tooling and supplies pages to ensure that all required objects exist in the GUI.  For instance, a sensor placement step requires an existing sensor tool, baseplate, sensor component tray, araldite batch, and so on.  Each of these objects must be created in its corresponding page; e.g. you must use the "Baseplates" page to create a baseplate B1 before you can use B1 to build a protomodule.

To create a part, navigate to the corresponding page, enter the desired part ID into the "ID" box, and click "New".  The part will not be fully created until you click "Save"; "Cancel" will discard the current changes.  "Load" will check to see whether a part exists, and if the part is found, all relevant data will be downloaded so you can view and edit it.  Parts may also be edited after creation with the "Edit" button, which will replace "New".  (If "Edit" is greyed-out, try pressing "Load" first.)

Tools and supplies may be created in a similar manner.  Note that protomodules and modules cannot be created using the Protomodules and Modules pages, only viewed, because they're automatically created upon completion of a sensor or PCB step.

Note that protomodules and modules are automatically created by the sensor placement and pcb placement steps, respectively.  They cannot be created manually, but can be edited after creation.  (Some protomodule/module information can't be inherited from their component parts, and has to be entered in manually.)

Currently, parts (baseplates, sensors, etc) can only be created locally, as DB communication has not been implemented yet.  After the API is ready, however, all baseplates, sensors, and PCBs should be entered into the DB prior to being shipped to MACs, and they must be downloaded by the GUI before they can be used for assembly.  Creation of those parts with the GUI will be disabled.

### Production steps and testing routines

Once all necessary information in the parts, tooling, and supplies section has been filled in, you can proceed to the production steps.  The production step pages are broadly similar to the previous ones, but with one major difference:  the data will be automatically checked for errors, and if any are found, a message explaining the problem will appear in the status box.  (For instance, entering in a nonexistent part or partially filling a row will produce errors.)  Once all errors have been resolved, you can save the step.

### Part search

To use the part search page, simply select the type of part you want to search for using the drop-down menu at the upper-left-hand corner, then select any other criteria you want using the options below.  You can then press "Search" to perform the query and display the results.  Lastly, you can jump to a part's info page by clicking on the part name in the "search results" box, then clicking the "Go to selected item" button underneath.

### XML generation (temporary)

Once a part (or a step in the case of protomodules and modules) has been created and saved, XML files formatted for the DB loader will be automatically generated  in the part's storage directory.  The storage directories are located at `SharedUI/filemanager_data/[part-name]/[creation-date]` by default.  As an example, the following files will be generated for a protomodule `PROTO_b1_s1`:

- filemanager_data/protomodules/6-28-2023/protomodule_PROTO_b1_s1_build_upload.xml
- filemanager_data/protomodules/6-28-2023/protomodule_PROTO_b1_s1_assembly_upload.xml
- filemanager_data/protomodules/6-28-2023/protomodule_PROTO_b1_s1_cond_upload.xml

Eventually, it will be possible to upload these XML files to the DB using the GUI.  For now, however, these files must be manually scp'ed to the DB loader (if you have the right permissions):

```
scp [filename].xml [cern-username]@dbloader-hgcal.cern.ch:/home/dbspool/spool/hgc/int2r
```

The GUI should ensure that the XML files are correctly formatted, so please let me know if you run into any errors in the DB loader logs.

**Note:  Currently, the HGCAL DB is not set up to accept conditions data for eight-inch modules.**  Consequently, you will not be able to upload the XML conditions ("cond") files for protomodules and modules.  (Hopefully we'll be able to fix this soon.)


## Instructions for developers

This section is intended for developers only, and ordinary users can safely ignore this section.

(Currently an outline, pending future architecture changes)

### GUI overview

![GUI structure](https://user-images.githubusercontent.com/53322354/234279465-5c297726-f480-40dd-97ca-77bf5f68c5c6.png)

In general:
- GUI receives data from:
   - Manual user input
   - Downloading from DB upon user prompting
   - Direct connection to lab software (TBD)
- GUI creates:
   - json files for:
      - local cache
      - longer-term, local storage at institution for data not stored in DB
   - xml files for uploading to DB loader
   - NOTE:  Currently planning to package the above w/ a custom-built software library

### Architecture

![GUI architecture](https://user-images.githubusercontent.com/53322354/234278118-5038d9ed-7e29-44b0-bb62-816cb76a5dd7.png)

- `mainUI.py`:  Entry point, runs main user interface window + manages page switching
   - UI defined by `main_ui/mainwindow.py`
   - `mainwindow.py` file generated from graphical `mainwindow.ui` file via compile.sh
- `pages/search.py`, `view_*.py`:  Manage user interaction/data updating/etc for each GUI page
   - UI defined by `pages_ui/search.py`, `view_*.py`
   - `*.py` files generated from graphical `*.ui` files via compile.sh
- `filemanager/*.py`:
   - Responsible for all data management
   - Defines classes for each object used in GUI (baseplate, sensor tool, PCB step, etc)
      - Each class has built-in new(), save(), load(), etc functions
   - Responsible for all json/xml generation, uploading, downloading, etc
      - Auto-created/saved/etc by built-in methods for each class
   - Also defines UserManager - class for tracking list of users at the institution (stored locally w/ json)

### Class structure for filemanager/fm.py

- fsobj:  Base class
   - fsobj\_tool:  Class for all tools
      - Sensor tool
      - PCB tool
      - Assembly tray
      - Sensor component tray
      - PCB component tray
   - fsobj\_supply:  Class for all supply batches
      - batch\_araldite
      - batch\_wedge
      - batch\_sylgard
      - batch\_bond\_wire
   - fsobj\_db:  Class for objects that can interact w/ DB (Note: may remove, merge properties into child classes)
      - fsobj\_part:  Class for parts used in assembly process
          - baseplate
          - sensor
          - pcb
          - protomodule
          - module
      - fsobj\_assembly:  Class for assembly steps
          - step\_sensor
          - step\_pcb

### Making changes to the user interface

It's recommended to use Qt Creator for editing the .ui files.  If it's not already installed, you can download it from the Qt Creator tab of [this page.](https://www.qt.io/offline-installers)  After making changes to the .ui files, run the script `compile.sh` (or `compile.bat`) in the .ui files' directory to carry all of the changes over to the corresponding .py files.  (Note:  Adding new .ui files will require you to modify compile.sh and compile.bat accordingly.)  Installing SQL Developer is also highly recommended for developers, since you may need to view the raw contents of the DB and test SQL queries.  You can download it [here.](https://www.oracle.com/database/sqldeveloper/technologies/download/)




