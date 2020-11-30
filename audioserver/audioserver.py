from flask import Flask, Response,render_template
import pyaudio, time, uuid


app = Flask(__name__)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
BITS_PER_SAMPLE = 16
DATA = None
TIME_INFO = None

def genHeader():
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (CHANNELS).to_bytes(2,'little')                                    # (2byte)
    o += (RATE).to_bytes(4,'little')                                  # (4byte)
    o += (RATE * CHANNELS * BITS_PER_SAMPLE // 8).to_bytes(4,'little')  # (4byte)
    o += (CHANNELS * BITS_PER_SAMPLE // 8).to_bytes(2,'little')               # (2byte)
    o += (BITS_PER_SAMPLE).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

def callback(in_data, frame_count, time_info, status):
    global DATA
    global TIME_INFO
    DATA = in_data
    TIME_INFO = time_info
    return (None, pyaudio.paContinue)

def listen():
  audio = pyaudio.PyAudio()
  stream = audio.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=callback)
  print("Stream started")
  return stream

@app.route('/audio')
def audio():
    header = genHeader()
    # start Recording
    def sound():
        try:
          print("Start audio stream")
          tinfo = None
          yield header + b'0'
          while True:
            yield DATA
            tinfo = TIME_INFO
            time.sleep(0)
        finally:
          print("End audio stream")

    return Response(sound(), headers={"Content-Type": "audio/x-wav"})

if __name__ == "__main__":
  stream = listen()
  app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)
  print("Cleaning....")
  stream.close()
