# rgagui

This Python application provides a graphic user intrface (GUI) environment 
to a suite of tests derived from the BaseTest class. 

A user can write a test as a prcedural program without considering interaction with GUI 
and run the test by adding it to a ".testdict" configuration file, 
and manage a test suite as a separeate GIT submodule, without modification of the rgagui core code.

A test uses pre-defined interfaces to interact with **rgagui** for user input, text output, real-time matplotlib plots, along with a remote command terminal to a device under test (DUT).
