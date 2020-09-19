from flask import Flask, Response,render_template
from threading import Thread
import pyaudio, time, uuid


app = Flask(__name__)

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 2048
BITS_PER_SAMPLE = 16

CLIENTS = {}

def listen():
  global DATA
  # define callback (2)
  def callback(in_data, frame_count, time_info, status):
      DATA = in_data
      return (DATA, pyaudio.paContinue)
    
  pya = pyaudio.PyAudio()
  stream = None
  def open():
    print("Open audio stream")
    return pya.open(format=FORMAT, 
                        channels=CHANNELS,
                        rate=RATE, 
                        input=True,
                        # stream_callback=callback,
                        frames_per_buffer=CHUNK)
  prev_data = None
  print("Start stream")
  while True:
    if not stream or not stream.is_active():
      stream = open()
    data = stream.read(CHUNK, exception_on_overflow = False)
    if prev_data != data:
      print("New data read")
    prev_data = data
    for k in CLIENTS:
      CLIENTS[k] = data
    time.sleep(1)

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

HEADER = genHeader()

def read_data(uid):
  while not CLIENTS[uid]:
    time.sleep(1)
  return CLIENTS[uid]

@app.route('/audio')
def audio():
    uid = str(uuid.uuid1())
    CLIENTS[uid] = None
    # start Recording
    def sound():
        print("%s start stream with %s" % (uid, HEADER))
        yield HEADER + b'0'
        while True:
            yield read_data(uid)
        print("%s disconnected" % uid)
        del CLIENTS[uid]
    return Response(sound(), headers={"Content-Type": "audio/x-wav"})

if __name__ == "__main__":
    Thread(target=listen).start()
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)