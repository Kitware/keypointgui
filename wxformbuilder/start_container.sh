image_name=wxformbuilder
container_name=wxformbuilder

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -z `docker ps -a -q -f name=^/${container_name}$` ]; then
  # If the container does not exist, start it.
  echo "Starting new container"

  # Maping /tmp/.X11-unix allows graphics to be passed.
  docker run --rm -dt \
    --network="host" \
  	-e DISPLAY=unix$DISPLAY \
    -v "/tmp/.X11-unix:/tmp/.X11-unix" \
    -v "/:/host_filesystem" \
    -v "$DIR/../georegistration_gui:/home/user/georegistration_gui" \
    --name $container_name \
    $image_name \
    /bin/bash
elif [ -z `docker ps -q -f name=${container_name}` ]; then
  # If the container exists but is stopped, start it.
  echo "Container is stopped, restarting it"
  docker start $container_name
else
  echo "Container already running"
fi
