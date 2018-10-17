# Simple OPC DA Datalogger <span style="color:red">(alfa)</span>
Simply desktop application to collect and record sensor values from an [OPC DA](https://en.wikipedia.org/wiki/OPC_Data_Access) server.

## 1) How to use
![Demonstraion](https://github.com/brunomsantiago/py_opcda_datalogger/raw/master/docs/py_opcda_datalogger_demo.gif "Simple OPC DA Datalogger demonstration")
- Run gui.py
- Choose and connect to an OPC DA server
- Choose which tags you want to record
- Click o Start Logging

## 2) Installation
#### 2.1) Python depedencies
- **[Python 2.7.](https://github.com/python/cpython/tree/2.7)** - I prefer using Python 3, however the OpenOPC library requires Python 2. I installed using conda
- **[Pywin32](https://github.com/mhammond/pywin32)** - I installed using conda
- **[OpenOPC](http://openopc.sourceforge.net/)** - Theoretically it is avaiable o [PyPi](https://pypi.org/project/OpenOPC/), but the installation using 'pip install OpenOPC' didn't worked for me. I had to cloning the repository and install it using 'pip install .'
- **Pyside** and **Qt4** - I installed using conda.

**Note:** For personal use I usually choose pyqt5, however for this little project I wanted to more permissive license.

#### 2.2) OPC DLL-module
The OpenOPC library need a registred OPC DLL-module to work (the [original from OPC Foundation](https://opcfoundation.org/developer-tools/samples-and-tools-classic) or any of the OPC vendors).
The easiest way is to download the [Graybox OPC DA Auto Wrapper is a DLL-module](http://gray-box.net/daawrapper.php) and follow the vende instructions:
> - download Graybox OPC DA Auto Wrapper;
> - unzip the archive;
> - copy gbda_aut.dll to Windows\System32 folder;
> - register this module - enter regsvr32 gbda_aut.dll in the command line.

**Notes**:
- OPC DA is very tied to Microsoft DCOM technology. So unfortunally this software is Windows only.
- It requires administrative permissions to register the DLL-module.
- Graybox allow free distribution of its dll, so it is also [avaiable in this repository](https://github.com/brunomsantiago/py_opcda_datalogger/blob/master/graybox_dll/graybox_opc_automation_wrapper.zip).

#### 2.3) OPC server
To use this Datalogger it is necessary to have a running OPC Server, either a real one from a SCADA System or a Simulation Server.
The develpment was done using [Matrikon Simulation Server](https://www.matrikonopc.com/products/opc-drivers/opc-simulation-server.aspx).

## 3) Motivation
I've written this software in my free time for personal use, specially to get better understand of OPC Classic.

However it might be useful for other people, so I decided tho share.

I don't intend to maintain in the long term nor give support.

## 4) License
I intend my own code to have the MIT License, however I haven't checked license compatibility with any of dependecies yet.

## 5) Next steps
#### 5.1) Soon
The software is working, however it very limited on options (I disabled them on the graphical interface).

It is also missing docstrings and unit tests.

I intend to work on these soon and maybe refactor some portions of the code and improve the graphical interface style.

#### 5.2) Maybe one day

I also would like to improve two things about this software, but don't know how to do.
- Make it portable with Nuikta
- Use timestamps with milliseconds precision (other OPC DA clients have this feature).
- Use the dll without registering thus not needing administrative permission.

Contibutions are very welcome.
