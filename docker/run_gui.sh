image_name=keypointgui
container_name=keypointgui

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/utilities.sh

# Open up xhost (for display) only to the container.
xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $container_name`

start_container $image_name $container_name

docker exec -it \
    -e "DISPLAY" \
   	-e "QT_X11_NO_MITSHM=1" \
    $container_name \
    /bin/bash -c "python /home/user/keypointgui/gui.py"

remove_container $container_name
