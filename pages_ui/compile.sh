#!/bin/bash
#Compile all .ui files using pyuic5 (for linux, must be able to run pyuic5 via the command line)

#pyuic5 input.ui -o output.py
echo "Working in directory:"
pwd
for f in "view_module" "view_baseplate" "view_sensor" "view_PCB" \
    "view_protomodule" "view_sensor_step" "view_sensor_post" \
    "view_pcb_step" "view_pcb_post" "view_tooling" "view_supplies" \
    "search" "view_wirebonding"\
    "view_plots" \
    "view_users" "../main_ui/mainwindow"
do
    command="pyuic5 $f.ui -o $f.py"
    eval $command
done
