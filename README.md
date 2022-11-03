# rgagui

**rgagui** is a Python application that provides a graphic user interface 
(GUI) environment to manage a suite of tasks running instruments. 

A user can write a task as a simple Python script and run the task 
by adding it to a ".taskconfig" configuration file, 
and manage a task suite as a separate package, without 
modification of the **rgagui** code.

A task uses pre-defined interfaces to interact with **rgagui** for user input, 
text output, real-time matplotlib plots, along with a remote command terminal 
to check instruments.

When it is installed from Test PyPI site, it does not install its dependency properly.
You may have to install Matplotlib and PyQt5 from the regular PyPI site:

    pip install pyqt5
    pip install matplotlib
    
Make sure you have the latest **rga** package version (>= 0.1.9) installed. 
You can upgrade it, it you are not sure.

    pip install -i https://test.pypi.org/simple/ rga --upgrade

After successful installation, you will see *rgagui.exe* in your 
Python/scripts directory. Make a shortcut for you convenience.

Make a copy of the example directory, Python/Lib/site-packages/rgagui/examples/rga100 
to you Documents directory.

Run rgagui.exe, click the menu/File/open config, and select the config file,
"myrga.taskconfig" in the example directory. 

Connect to an RGA, from the menu/Control, and select a task and press run button from the tool bar.

From the terminal window, type 'dut.dir' to see available components, 
commands, and methods. Type the following to see how it changes:

    dut.scan.dir
    dut.scan.initial_mass    
    dut.scan.initial_mass = 10
    dut.scan.initial_mass   

Look through the Task config file to see how to organize instruments and tasks.
In the file, the line with 'name:' appears as the **rgagui** window title, 
the lines with 'inst:' are the instruments you will use, 
and lines with 'task:' show in the rgagui menu bar under the menu/Tasks.

Review the task files in the rga100/tasks directory to see how to a script written.

Write your own tasks for test and measurement!

