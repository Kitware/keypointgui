container_name=wxformbuilder

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/start_container.sh

# Open up xhost (for display) only to the container.
xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $container_name`

docker exec -it \
    -e "DISPLAY" \
   	-e "QT_X11_NO_MITSHM=1" \
    $container_name \
    /bin/bash

source $DIR/stop_container.sh
