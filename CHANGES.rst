0.6
---
- Don't display VNC link in machine view if machine is not running
- Add missing os.path import to net model
- Add empty record to cpu_types, machine_types, and nic_types tables to allow for unselected types while still maintaining ForeignKey contraint
- Add missing os.path include
- Split unwieldy models.py module into its own sub-package
- Clean up models - add CASCADE logic, emit appropriate PRAGMA for ForeignKey-relates constraints in sqlite3 \(Does anyone have a better method than what I\'ve got going on in __init__.py and initializedb.py?\)
- Correct issue with SQLA returning None as Model.netnone instead of boolean
- Set tooltips for *Grid to something more descriptive
- Link header to main page
- Make cmdline output wrap if necessary
- Pull layout css from 520035d0de commit
- Fix VDE reference issue in NetForm
- Fix DriveGrid and NetGrid not filtering on correct column. Fix ViewClass.grid not applying filter criteria correctly
- Add TightVNC jar file that got ignored by a git rule. Add links to the VNC viewer directly in the MachineGrid widget
- Merge in master changes
- Merge branch 'applet'
- Add initial VNC viewer support via TightVNC applet
- Add initial VNC viewer support via TightVNC applet
- Merge master back into branch
- Make cmdline output wrap. Remove printf debug that accidentally made its way into the tree
- Grids: Make boolean columns display check-boxes
- Abstract JSON generator code for grid views into parent class. Add paging and sorting code
- Layout cleanup. Add header-bar image
- Added status column to VDE grid
- Convert MachineGrid from SQLAjqGridWidget to jqGridWidget. Add related json view - provide machine status
- Require Python >= 2.7
- Fixed child processes holding server socket FD after spawn. Return error code if process is already running
- Merge launcher branch
- Abstract launch methods into separate Launchable mix-in. Add launch capability to VDE grid and models. (Code - bugs) can now do all the things my original shell scripts did.
- Added GUI machine launch.
- Added Flash message processing to master template and related CSS
- Removed egg-info accidentally included in VCS
- Removed egg-info accidentally included in VCS
- Reverted model args and cmdline to properties. Created PathConfig class in models.py as a configuration mixin for models. Revert machine view to use properties as above. Added basic launch capability to Machine model.
- Model .args and .cmdline changed from property to method accepting settings dict. Remove broken ConfiguredBase class. Model .args methods altered to abide by .ini settings. Add missing "index" flag to drive args. Change vde_ports to vde_socks in config files.
- Modify cmdline in machine view to display in broken line format
- Model args property now produces a tuple for each argument set. Modify Base class to accept configuration dict parameter
- Fix initializedb script pulling configuration data from incorrect key
- Add qtubes-specific configuration data to default configuration files. Update production.ini to more closely match development.ini
- Reformat CHANGES.rst to be in common inverse order. Change footer on master template to GPL style
- Minor layout updates. Add command-line visualization for debugging. Correct Net->VDE relation in model.
- Make edit widgets pull dynamic option data from tables at display time + Minor UI updates

0.5
---
- Add VDE grid and editing support
- Add initial Net editing capability
- Added NetGrid and related Net views
- Further consolidation of Net* models into Net model. Correct resultant
  issues in initializedb script.
- Code cleanup in views.py. Add delete view for Drive and enable in related
  widget. Refactor Net* models into unified Net model
- Removed broken requirement in setup.py
- Minor docstring update and cleanup
- Converted DriveEdit widget to TableForm, moved validation to drive_edit view
- Refactored MachineEdit widget to use tw2.forms.TableForm, and modified 
  machine_edit view to handle validation and DB fetching
- Revert development.ini to something a little more sane
- Fix typo in views.py, add *.genshi files to MANIFEST

0.4
---

- Correct README - add #tubes selector to initialize_Tubes_db example
  to correct issue with pserve looking in the wrong place for db url.
  See this thread: 
  https://groups.google.com/forum/?fromgroups=#!topic/pylons-discuss/XNYNq2ietsw
  Clean up views.py - convert to class-based views. Remove cruft.

0.3
---

- Initial Drive editing and Drive Grid widgets completed.

0.2
---

- Initial machine grid completed, along with simple machine
  editing capability.

0.1
---

- Basic models for Machine, Drive, and Net* completed.

0.0
---

-  Initial version
