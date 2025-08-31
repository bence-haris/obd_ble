#!/bin/bash

# OBD2 Value Reader
# Usage: ./scan_obd.sh -a [MAC_ADDRESS] -c [COMMAND]

# -a "81:23:45:67:89:BA"
#HEX_COMMAND="30313043300d"  # Default: Clear Echo

while getopts "a:c:" opt; do
        case $opt in
                a)
                        MAC_ADDRESS=$OPTARG
                        ;;
                c)
                        case $OPTARG in
                            rpm)
                                HEX_COMMAND="30313043300d"
                                command="rpm"
                                ;;
                            *)
                                echo "Function not implemented yet. Defaulting to 'Clear Echo'"
                                HEX_COMMAND="415445300d"
                                command="test"
                                ;;
                        esac
                        ;;
                *)
                        echo -e "Invalid option.\n-a: MAC Address of device\n-c: Command";
                        exit 1
                        ;;
        esac
done





# Function to calculate RPM from response
calculate_rpm() {
    local raw_string="$1"
    # Extract hex bytes after "41 0C"

    local raw_value=${raw_string:4}
    local byte_high=${raw_value:0:2}
    local byte_low=${raw_value:2}

    local dec_high=$((0x$byte_high))
    local dec_low=$((0x$byte_low))

    rpm=$(( (dec_high * 256 + dec_low) / 4 ))
}

# Use interactive mode to get the response
result_encoded=$({
    echo "connect"
    sleep 3
    echo "char-write-req 0x000d $HEX_COMMAND"
    sleep 3  # Wait for ELM327 to respond
    echo "exit"
    sleep 3
} | gatttool -b "$MAC_ADDRESS" -I 2> /dev/null | grep "Notification" | awk -F "value: " '{print $2}')


result_decoded=$(echo $result_encoded | xxd -r -p | tr -d '\r\n> ')

echo "Value on $MAC_ADDRESS for $command is $result_decoded"

if [[ $command == "rpm" ]];then
    rpm=0
    calculate_rpm "$result_decoded"
    echo "RPM is $rpm"
else
    echo $result_decoded
fi
