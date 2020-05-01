#!/bin/bash
#Compile all .ui files using pyuic5 (for linux, must be able to run pyuic5 via the command line)

#pyuic5 input.ui -o output.py

for f in "view_module" "view_baseplate" "view_sensor" "view_PCB" \
    "view_protomodule" "view_kapton_step" "view_sensor_step" \
    "view_pcb_step" "view_tooling" "view_supplies" \
    "view_shipment" "routine_iv"
do
    command="pyuic5 $f.ui -o $f.py"
    eval $command
done
