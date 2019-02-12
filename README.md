# openvas_py_cli
Python script for interacting with OMP v. 2

This script was created for the sole purpose of making it easy to read the results of an OpenVAS report from within a terminal.
The python script utilizes the OpenVAS OMP Command Line Interface in order to output a text formatted report. The default output from OMP for a text formatted report is XML with the body of the report base64 encoded.

Since base64 is hard for (most) humans to read this script makes things a bit easier.
It is currently in a very rough state and under development when I feel like it.

Some future plans for this script are to modify it to accept command line arguments, and to modify it to allow full control of more creative OpenVAS functions from the command line.

Ultimately the openvas-omp.rb project really should be updated and this should just become a way to read reports...

