
Writing a task script
-----------------------

When you write a Python script that runs with ``srsgui``, you make a subclass of
:class:`Task <srsgui.task.task.Task>` class, and implement
:meth:`setup<srsgui.task.task.Task.setup>`,
:meth:`test<srsgui.task.task.Task.test>` and
:meth:`cleanup<srsgui.task.task.Task.cleanup>`.

Following is the simplest form of a task. Even though it does not do much,
``srsgui`` is happy to run the task, if it is included in a .taskconfig file.

.. _top-of-bare-bone-task:

.. code-block::

    from srsgui import Task

    class ZerothTask(Task):
        def setup(self):
            print('Setup done.')

        def test(self):
            print('Test finished.')

        def cleanup(self):
            print('Cleanup done.')

When a task runs, the setup() method runs first. if the setup finished with an exception,
the task is aborted without running test() or cleanup(). If the setup() method completes
without exception, the test() method runs next. Regardless of exception happened while
the test() is finished, running the cleanup() method completes the task.

You write a task based on the template any way you want, utilizing the resources and APIs
provided in Task class for Graphic User Interface (GUI) inputs and outputs. As long as
your tasks use the limited GUI resources available from Task class,
your task will run along with ``srsgui`` application.

A task is a Python thread_ (if it is run by an application with a Qt backend,
it will be QThread_.), running as concurrently with the main application.

The :class:`Task <srsgui.task.task.Task>` is designed with much consideration
on protection of the main application from crashing caused by unhandled Exception,
while a buggy task running. ``srsgui`` provides information as much as Python
interpreter does. After modifying a task, reopen the .taskconfig file will reload
the modified task before you run it again.


The main application provides resources that a task can use,
and responds to the callbacks from the task. The resources are set using
the APIs provided by the task.

    - :meth:`set_inst_dict <srsgui.task.task.Task.set_inst_dict>` is to set the
      instrument dictionary that contains the instrument instances.
    - :meth:`set_data_dict <srsgui.task.task.Task.set_data_dict>` is to set the
      data dictionary that contains the data instances.
    - :meth:`set_figure_dict <srsgui.task.task.Task.set_figure_dict>` is to set the
      figure dictionary that contains the figure instances.
    - :meth:`set_session_handler <srsgui.task.task.Task.set_session_handler>` is
       to set the session handler that saves the data to a file.
    - :meth:`set_callback_handler <srsgui.task.task.Task.set_session_handler>` is
      to set the callback handler that handles the callbacks from the task.


The main application and the running task are separate threads, and the main application responds only to
the callbacks from the task.

For text output,
    - :meth:`write_text <srsgui.task.task.Task.write_text>` is the base method for Task to use
      :meth:`callbacks.text_available <srsgui.task.callbacks.text_available>` callback.
    - :meth:`display_device_info <srsgui.task.task.Task.display_device_info>`
    - :meth:`display_result <srsgui.task.task.Task.display_result>`
    - :meth:`update_status <srsgui.task.task.Task.update_status>`
    - :meth:`print <srsgui.ui.taskmain.TaskMain.print_redirect>`

For python logging_,
    - :meth:`get_logger <srsgui.task.task.Task.get_logger>` is to get the logger instance for the task.
    - ``logger.debug`` is to use the logger instance to log debug messages.
    - ``logger.info`` is to use the logger instance to log info messages.
    - ``logger.error`` is to use the logger instance to log error messages.
    - ``logger.warning`` is to use the logger instance to log warning messages.
    - ``logger.critical`` is to use the logger instance to log critical messages.


For the input panel in the ``srsgui`` main window,
    :attr:`input_parameters <srsgui.task.task.Task.input_paramteres>` is a dictionary that contains
    the input parameters that will be displayed in the input panel.

    - :meth:`get_all_input_parameters <srsgui.task.task.Task.get_all_input_parameters>` is to get all the input
      parameters that are displayed in the input panel.
    - :meth:`set_input_parameter <srsgui.task.task.Task.set_input_parameter>` is to set the value of an input
      parameter.
    - :meth:`get_input_parameter <srsgui.task.task.Task.get_input_parameter>` is to get the value of an input
      parameter.
    - :meth:`notify_parameter_changed <srsgui.task.task.Task.notify_parameter_changed>` is a wrapper method for
      :meth:`callbacks.parameter_changed <srsgui.task.callbacks.parameter_changed`, which is to notify the
      main application that the value of an input parameter has changed. The main application will
      update the value of the input parameter in the input panel.

For Matplotlib Figures,

    callbacks.request_figure_update - draw
    callbacks.notify_data_available - update
    clear_figure
    get_figure

For a question dialog box during running a task,
    - :meth:`ask_question <srsgui.task.task.Task.ask_question>` is a wrapper method
      for the Task :meth:`callbacks.new_question <srsgui.task.callbacks.new_question>`.
    - :meth:`question_background_update <srsgui.task.task.Task.question_background_update>`


For the session_handler that save information from a task to a file,
    add_details
    create_table
    add_data_to_table
    create_table_in_file
    add_to_table_in_file

For inst_dict
    - :meth:`get_instrument <srsgui.task.task.Task.get_instrument>` is to retrieve
      the Instrument subclass instance named in the \.taskconfig file. Once getting
      the instrument instance, you can use it in the task in the same way with
      the instance created from a Python interpreter.

Once you get used to the APIs of Task class, you can write scripts that runs
as a part of ``srsgui``.


.. _PyVisa: https://pyvisa.readthedocs.io/en/latest/
.. _srsinst.sr860: https://pypi.org/project/srsinst.sr860/
.. _VXI11: https://www.lxistandard.org/About/VXI-11-and-LXI.aspx
.. _GPIB: https://en.wikipedia.org/wiki/IEEE-488
.. _USB-TMC: https://www.testandmeasurementtips.com/remote-communication-with-usbtmc-faq/
.. _thread: https://realpython.com/intro-to-python-threading/
.. _QThread: https://doc.qt.io/qt-6/qthread.html
.. _logging: https://docs.python.org/3/howto/logging.html