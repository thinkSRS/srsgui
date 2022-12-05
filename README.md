# rgagui

**rgagui** is a Python application that provides a graphic user interface 
(GUI) environment to manage a suite of tasks that interact with instruments. 

A user can write a task as a simple Python script and run the task 
by adding it to a ".taskconfig" configuration file, 
and manage a task suite as a separate package, without 
modification of the **rgagui** code.

A task uses pre-defined interfaces to interact with **rgagui** for user input, 
text output, real-time matplotlib plots, along with a remote command terminal 
to controls instruments.
