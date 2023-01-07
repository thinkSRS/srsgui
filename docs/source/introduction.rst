

First Example
==============

Let's make the first example using Srsgui. I happened to have a Siglent SDS1202X-E oscilloscope and a Stanford Research Systems CG635 2.5 GHz Synthesized Clock Generator on my desk. The oscilloscope has raw TCPIP socket, VXI11, and USB TMC communication interfaces available. The clock generator has RS232 serial and GPIB communication interface. There are 5 different communication protocol is available to talk to the instruments. Srsgui supports all these communication interfaces. As a default, Srsgui supports serial and tcpip interfaces, because it uses Pyserial for serial communication and Python built-in socket for TCPIP communication. 

There are VXI11 interface using python-vxi11 package and and VISA interface using PyVisa available in srsinst.sr860 package.

Python's extensive availablilty of various libraries makes easy to build an application without reinventing the wheels.

As the first step, let's make the oscilloscope and the clock generator usable in Srsgui from the scratch.


As the first step, let's create directories and empty files as shown below. 

    /first example directory
        /instruments
            sds1202.py
            cg635.py           
        /tasks
            first.py
            second.py         
        firstexample.taskconfig


We have two instrument driver scripts in the subdirectoty called instruments, two task scripts in the subdirectory called tasks, and a configuration file to tell Srsgui how to use them in the project root directory. Python does not allow to use spaces in its package and module names. Use underscore if you need spaces between words.

Instument drivers
-------------------



.taskconfig 
------------





        