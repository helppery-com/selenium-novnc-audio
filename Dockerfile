FROM nurdism/neko:firefox

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

# RUN NoVNC
COPY supervisord.conf /etc/supervisor/conf.d/zzz_hmihy.conf

EXPOSE 6080 4444 5900 5000