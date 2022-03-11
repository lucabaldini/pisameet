
Raspberry PI Configuration
==========================




Basic installation
------------------

The SD card that comes with the raspberry PI has
`raspbian <https://www.raspberrypi.com/software/operating-systems/>`_ pre-installed.
You can figure out the particular raspbian version by doing

.. code-block::

   > less /etc/os-release

   PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"
   NAME="Raspbian GNU/Linux"
   VERSION_ID="9"
   VERSION="9 (stretch)"
   ID=raspbian
   ID_LIKE=debian
   HOME_URL="http://www.raspbian.org/"
   SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
   BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"

In order to update to the latest version, go ahead and download the OS image from the
`raspberry page <https://www.raspberrypi.com/software/operating-systems/>`_
and unzip it.

The community recommends `Etcher <https://www.balena.io/etcher/>`_ to flash the
image onto the SD card, and this is actually quite easy---you download the
binary from the website, change the permissions to make it executable and
run it. (You will need a card reader for the thing to happen.)

.. note::

   Version 11 of raspbian comes with Python 3.9.2 installed, and it seems like
   a good starting point for our purposes.

After the OS installation you might want to do an update:

.. code-block::

   > sudo apt dist-upgrade


Dependencies
------------

The only additional package that you need, on top of the standard raspbian
Desktop installation, is the Python wrappers to the Qt library for the GUI.

.. code-block::

   > sudo apt-get install python3-pyqt5



Setting up the screen
---------------------

You get control of the screen orientation (e.g., vertical vs. horizontal) through
the `Preferences -> Screen Configuration` dialog. This will open the screen
editor that allows to change the orientation.

Alternatively, you can hack the ``/boot/config.txt``, e.g.

.. code-block::

    display_hdmi_rotate=1

to rotate the screen by 90 degrees (i.e., to the right).


Presentation software
---------------------

In order to clone the repository just do

.. code-block::

   > git clone https://github.com/lucabaldini/pisameet.git

