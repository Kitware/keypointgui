image_name=keypointgui
container_name=keypointgui

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if ! [ -z `docker ps -a -q -f name=^/${container_name}$` ]; then
  docker stop $container_name
fi

if ! [ -z `docker ps -q -f name=${container_name}` ]; then
  docker rm $container_name
fi
