#!/bin/bash

# usage:  bash install_dependencies.sh /path/to/install/dir
# Note that the install directory can be anywhere on your machine,
# including outside of the GUI (SharedUI) repository.
# If no install directory is given, software will be installed to
# the current directory.

INSTALL_DIR="${1:-thisdir}"
if [ $INSTALL_DIR = 'thisdir' ]
then
  INSTALL_DIR=$(pwd)
fi

cd $INSTALL_DIR

# first, clean any previous installations in this directory:
rm -rf instantclient* cmsdbldr
# if ic exists in environment script, don't add redundancies:
if grep -sq instantclient ~/.bash_profile || \
   grep -sq instantclient ~/.bashrc || \
   grep -sq instantclient ~\.bashrc
then
    RCPATH=1  # found previous instantclient path in bashrc
else
    RCPATH=0
fi


# auto-install oracle stuff for mac
# UNAME ALT:  https://megamorf.gitlab.io/2021/05/08/detect-operating-system-in-shell-script/
unameOut="$(uname -s)"

echo 'TESTING:  unameOut is '$unameOut

case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    msys*)      machine=Windows;;
    WindowsNT*) machine=Windows;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac


echo 'NOTE:  This install script requires OSX, Windows, or Linux.'
echo 'x86-64 is assumed for each of the above.'

if [ $RCPATH == 1 ]
then
  echo 'WARNING:  InstantClient path found in .bashrc/.bash_profile.  PATH will not be udpdated.'
  echo 'If you have previously installed an older version of InstantClient, please make sure to'
  echo 'remove the corresponding lines from your ~/.bashrc or ~/.bash_profile before running'
  echo 'this script again.  Otherwise, ignore this warning.'
fi

echo 'Installing python modules...'

# install the easy stuff first
python -m pip install ilock numpy PyQt5 requests cx_Oracle

echo 'Done.'
echo 'Installing cmsdbldr...'

# Install and auto-add to PATH
git clone https://github.com/valdasraps/cmsdbldr.git
if [ $RCPATH == 1]
then
  if [ $machine = "Mac" ]
  then
    echo "# Module assembly GUI software:" >> ~/.bash_profile
    echo "export PYTHONPATH=${INSTALL_DIR}/cmsdbldr/src/main/python:\$PYTHONPATH" >> ~/.bash_profile
  elif [ $machine = "Linux" ]
  then
    echo "# Module assembly GUI software:" >> ~/.bashrc
    echo "export PYTHONPATH=${INSTALL_DIR}/cmsdbldr/src/main/python:\$PYTHONPATH" >> ~/.bashrc
  elif [ $machine = "Windows" ]
  then
    echo "# Module assembly GUI software:" >> ~\.bashrc
    echo "export PYTHONPATH=${INSTALL_DIR}\\cmsdbldr\src\main\python:\$PYTHONPATH" >> ~/.bashrc
  else
    echo 'ERROR:  could not auto-append the install directory to your $PYTHONPATH'
    echo 'in .bashrc/.bash_profile/etc (OS incompatible).'
    echo 'Please add '$INSTALL_DIR'/cmsdbldr to your $PYTHONPATH manually.'
  fi
fi

echo 'Installing Oracle InstantClient...'

if [ $machine = "Mac" ]
then
  curl https://download.oracle.com/otn_software/mac/instantclient/instantclient-basic-macos.zip --output instantclientTMP.zip
  unzip instantclientTMP.zip
  curl https://download.oracle.com/otn_software/mac/instantclient/instantclient-sqlplus-macos.zip --output instantclientBIN.zip
  unzip instantclientBIN.zip
  rm instant*.zip

  # get (version-dependent) directory name
  export ICDIR=$(find instantclient_* -maxdepth 0 -type d)
  if [ $RCPATH == 1]
  then
    # Add to PATH via adding a new line to .bash_profile
    echo "export PATH=${INSTALL_DIR}/${ICDIR}:\$PATH" >> ~/.bash_profile
    echo "export INSTANT_CLIENT_HOME=${INSTALL_DIR}/${ICDIR}" >> ~/.bash_profile
  fi
  source ~/.bash_profile

elif [ $machine = "Linux" ]
then
  curl https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linuxx64.zip --output instantclientTMP.zip
  unzip instantclientTMP.zip
  curl https://download.oracle.com/otn_software/linux/instantclient/instantclient-sqlplus-linuxx64.zip --output instantclientBIN.zip
  unzip instantclientBIN.zip
  rm instant*.zip

  # get version
  export ICDIR=$(find instantclient_* -maxdepth 0 -type d)
  if [ $RCPATH == 1]
  then
    # Add to PATH via adding a new line to .bash_profile
    echo "export PATH=${INSTALL_DIR}/${ICDIR}:\$PATH" >> ~/.bashrc
    echo "export INSTANT_CLIENT_HOME=${INSTALL_DIR}/${ICDIR}" >> ~/.bashrc
  fi
  source ~/.bashrc

elif [ $machine = "Windows" ]
then
  echo 'WARNING:  Assuming Windows x64.  This InstantClient verison will not work for 32-bit architectures.'
  echo 'For Windows 32, please visit the following webpage, choose your OS, then scroll to the bottom and follow the'
  echo 'directions for installing the basic package:'
  echo 'https://www.oracle.com/database/technologies/instant-client/downloads.html'
  echo 'NOTE:  Then install the SQL*Plus Package as well.'
  echo 'Proceeding with x64 installation...'

  curl https://download.oracle.com/otn_software/nt/instantclient/instantclient-basic-windows.zip --output instantclientTMP.zip
  unzip instantclientTMP.zip
  curl https://download.oracle.com/otn_software/nt/instantclient/instantclient-sqlplus-windows.zip --output instantclientBIN.zip
  unzip instantclientBIN.zip
  rm instant*.zip

  # get version
  export ICDIR=$(find instantclient_* -maxdepth 0 -type d)
  # Add to PATH via setx (WARNING: Requires Windows 7 or later, currently untested)
  # setx /M path "%path%;"$INSTALL_DIR'\'$ICDIR
  # FOR NOW:  Attempt to add to bashrc
  if [ $RCPATH == 1]
    echo "export PATH=${INSTALL_DIR}/${ICDIR}:\$PATH" >> ~\.bashrc
    echo "export INSTANT_CLIENT_HOME=${INSTALL_DIR}/${ICDIR}" >> ~\.bashrc
  fi
  source ~\.bashrc

else
  echo 'ERROR:  Sorry, cannot auto-install Oracle InstantClient for the detected OS.'
  echo 'Please visit the following webpage, choose your OS, then scroll to the bottom and follow the'
  echo 'directions for installing the basic package:'
  echo 'https://www.oracle.com/database/technologies/instant-client/downloads.html'
  echo 'NOTE:  Then install the SQL*Plus Package as well.'
fi

echo ''
echo 'Installation finished.  Please check the output above for errors or warnings.'


cd -


