image_name=keypointgui
container_name=keypointgui_pykernel

# Ipython kernel name.
kernel_name=remote_kernel_keypointgui.json

# Location on host to save remote Ipython kernels to.
host_kernel_dir=$(jupyter --runtime-dir)/remote_keypointgui_kernels
#host_kernel_dir=/run/user/1000/jupyter/

# Location of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/utilities.sh

# Open up xhost (for display) only to the container.
xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $container_name`

# If the container does not exist, start it.
echo "Starting new IPython kernel container"

# Maping /tmp/.X11-unix allows graphics to be passed.
docker run --rm -it \
  --network="host" \
	-e "DISPLAY" \
 	-e "QT_X11_NO_MITSHM=1" \
  -v "/tmp/.X11-unix:/tmp/.X11-unix" \
  -v "$DIR/../data:/home/user/data" \
  -v "$DIR/../keypointgui:/home/user/keypointgui" \
  -v "/:/host_filesystem" \
  -v "$host_kernel_dir:/home/user/.local/share/jupyter/runtime" \
  --name $container_name \
  $image_name \
  /bin/bash -c "cd ~/keypointgui && sudo /home/user/miniconda/bin/python -m spyder_kernels.console --pylab=auto --matplotlib=auto -f $kernel_name"

# python -m spyder_kernels.console --pylab=auto --matplotlib=auto -f remote_kernel_keypointgui.json
# -c "python -m spyder_kernels.console --pylab=auto --matplotlib=auto -f $kernel_name"

# Use command '%matplotlib auto' within the remote console so that plots are not
# inline.

remove_container $container_name
