# ``Srsgui`` - Organize instrument-controlling Python scripts as a GUI application

`Srsgui` is a simple framework:

   - To define instrument classes for instruments that use remote communication,
     based on `Instrument` class and the communication `Interface` class 
     (By default, serial and TCPIP is available. VXI11, GPIB and USB-TMC are optional.).

   - To write Python scripts (tasks) that run in GUI environment with simple APIs
     provided in ``Task`` class.

   - To organize instrument classes and task scripts presented in a GUI application
     using a configuration (.taskconfig) file for a project

![screenshot](https://thinksrs.github.io/srsgui/_images/example-screen-capture-2.png " ")

## Installation

To run ``srsgui`` as an application, create a virtual environment, if necessary, 
and install using ``pip`` with [full] option:  

    python -m pip install srsgui[full]

``Srsgui`` package has the following 3 main dependencies: 
[pyserial](https://pypi.org/project/pyserial/), 
[matplotlib](https://pypi.org/project/matplotlib/) and
[PySide6](https://pypi.org/project/PySide6/). If the installation above fails, 
you have to install the failed pacakge manually. Using a virtual environment will
eliminate possible conflicts between packages in the main Python installation and 
the packagesSome used in `srsgui`. Some Linux distributions offer 
some of the Python packages from their repositories only, not from ``pip``. 
Run web search for more information on system-specific installation.   

Once pyserial, matplotlib and PySide6 are installed properly, or you plan to use
`srsgui` for instrument drivers only without GUI support, 
you can install ``srsgui`` without [full] option:

    python -m pip install srsgui

## Start ``srsgui`` application
    
if the Python Script directory is in PATH environment variable,
Start the application by typing from the command line:

    srsgui

If the script directory is not in PATH, run the srsgui module with Python. 

    python -m srsgui
    
It will start `srsgui` application.

## Run the example project

By default, `srsgui` application starts with the last project it ran,
when it is closed.
 
To open the example project included in the `srsgui` package 
(if `srsgui` does not start with the example project), select the menu/File/Open config, 
go to the `srsgui` package directory, find the examples directory, and find a .taskconfig file
in the example project folder. 

You can run the second and fifth task in the Task menu 
even without any instruments connected.

## Create a project

`Srsgui` is a framework to helps you to write your own instrument-controlling 
Python scripts running as a GUI application. Using its APIs, you can write 
scripts running in GUI with the same amount of code with writing console-based 
scripts. For programming API, refer to
[`srsgui` documentation](https://thinksrs.github.io/srsgui).
