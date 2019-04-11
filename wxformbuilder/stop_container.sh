image_name=wxformbuilder
container_name=wxformbuilder

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if ! [ -z `docker ps -a -q -f name=^/${container_name}$` ]; then
  docker stop $container_name
fi

if ! [ -z `docker ps -q -f name=${container_name}` ]; then
  docker rm $container_name
fi
