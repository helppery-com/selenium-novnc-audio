#!/bin/bash

export ENVIRONMENT=${1:-dev}
export SEL_PORT=4444
export NOVNC_PORT=6080
export AUDIO_PORT=5000

if [ "dev" == "$ENVIRONMENT" ]; then
  export SEL_PORT=4445
  export NOVNC_PORT=6081
  export AUDIO_PORT=5001
fi

echo "Push changes"
git push

echo "Pull changes"
ssh hetzner "cd /root/selenium-novnc-audio && git pull"

echo "build docker image"
ssh hetzner "cd /root/selenium-novnc-audio && docker build -t helppery/selenium-novnc-audio ."

echo "Run container"
ssh hetzner "docker rm -f selenium-novnc-audio-$ENVIRONMENT"
ssh hetzner "docker run -d --name selenium-novnc-audio-$ENVIRONMENT -p $NOVNC_PORT:6080 -p $SEL_PORT:4444 -p $AUDIO_PORT:5000 -v /dev/shm:/dev/shm --privileged --cap-add=ALL -it -v /dev:/dev -v /lib/modules:/lib/modules helppery/selenium-novnc-audio"