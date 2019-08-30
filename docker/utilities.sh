# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


function remove_container()
{
  container_name=$1

  if ! [ -z `docker ps -a -q -f name=^/${container_name}$` ]; then
    docker stop $container_name
  fi

  if ! [ -z `docker ps -q -f name=${container_name}` ]; then
    docker rm $container_name
  fi
}


function start_container()
{
  image_name=$1
  container_name=$2

  if [ -z `docker ps -a -q -f name=^/${container_name}$` ]; then
    # If the container does not exist, start it.
    echo "Starting new container"

    # Maping /tmp/.X11-unix allows graphics to be passed.
    docker run --rm -dt \
      --network="host" \
    	-e "DISPLAY" \
      -v "/tmp/.X11-unix:/tmp/.X11-unix" \
      -v "$DIR/../data:/home/user/data" \
      -v "$DIR/../keypointgui:/home/user/keypointgui" \
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
}
