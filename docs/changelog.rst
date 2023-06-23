Changelog
==========
V.0.4.0 -- Jun 21, 2023
    * Changed :mod:`IndexCommand <srsgui.inst.indexcommands>`
      to instance variable to handle multiple instances correctly.
      It requires a subclass of IndexCommand to be defined in __init__() of the subclass.
      self.add_parent_to_index_commands() should be called after the definition of index commands.

V.0.3.4 -- Jun 20, 2023
    * Removed default_value from :class:`CommandInput <srsgui.task.inputs.CommandInput>`.__init__.
      cmd_instance argument is not necessary, either.

V.0.3.1 -- May 22, 2023
    * Changed task result file name extension to .sgdata.

V.0.3.0 -- May 16, 2023
    * Moved documentation to Github Pages.
    * Added boilerplate license header to source files.
    * Added the changelog and troubleshoot pages to documentation.



