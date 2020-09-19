FROM selenium/standalone-firefox-debug:3.141.59-20200525

USER seluser

RUN sudo apt update && \
    sudo apt-get install -y git python3-pip libasound-dev && \
    sudo apt-get install -y portaudio19-dev libportaudio2 libportaudiocpp0 && \
    sudo apt-get install -y ffmpeg

# Clone noVNC.
RUN git clone https://github.com/novnc/noVNC.git $HOME/noVNC
RUN cp $HOME/noVNC/vnc.html $HOME/noVNC/index.html

# websockify
RUN git clone https://github.com/kanaka/websockify $HOME/noVNC/utils/websockify

# Audio server
RUN pip3 install pyaudio flask
COPY audioserver $HOME/audioserver
RUN pip3 install -r $HOME/audioserver/requirements.txt

# RUN NoVNC
COPY supervisord.conf /etc/supervisor/conf.d/zzz_hmihy.conf
#COPY start-vnc.sh /opt/bin/
COPY fluxbox.init /usr/share/fluxbox/init

#RUN $HOME/noVNC/utils/launch.sh --vnc localhost:5900 &

EXPOSE 6080 4444 5900 5000