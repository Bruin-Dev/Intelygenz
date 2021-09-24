#!/bin/bash

# first set your env to KRE_BASE_URL=kre-host:9000 

if [ $# -eq 0 ]
  then
    echo "Missing first argument. Entrypoint kre version."
    exit 1
fi

check_not_empty() {
  VARNAME=$1
  ERR=${2:-"Missing variable $VARNAME"}
  eval VALUE=\${$VARNAME}

  [ "$VALUE" != "" ] || (echo $ERR && exit 1)
  return 0
}

close_port_forward() {
  # STOPPING PORT FORWARD
  echo "closing port forward..."
  {
    sleep 0.2 && kill -s INT $PORT_FORWARD_PID && wait $PORT_FORWARD_PID
  } &
}
trap close_port_forward INT

export KREHOST=$(ifconfig | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" | grep -v 127.0.0.1 | awk '{ print $2 }' | cut -f2 -d: | head -n1)
export NAMESPACE=kre
export VERSION=rta-$1

echo "opening port forward to entrypoint..."
ENTRYPOINT_POD=$(kubectl -n $NAMESPACE get pod -l version-name="$VERSION",type=entrypoint -o custom-columns=":metadata.name" --no-headers)
check_not_empty "ENTRYPOINT_POD" "missing entrypoint pod. Check Kubernetes namespace. Used $NAMESPACE"
kubectl port-forward "$ENTRYPOINT_POD" --address=$KREHOST 9000:9000 -n $NAMESPACE &
PORT_FORWARD_PID=$?
echo "portforward pid " $PORT_FORWARD_PID

docker-compose build repair-tickets-monitor repair-tickets-kre-bridge && docker-compose up repair-tickets-monitor repair-tickets-kre-bridge