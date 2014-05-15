from gevent import spawn
from gevent.event import Event
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort
from traceback import format_exc
from gevent import socket
import struct, sys, logging, logging.handlers

logger = logging.getLogger("fft-server")
logger.setLevel("WARN")
#logger.addHandler(logging.StreamHandler(sys.stdout))
handler = logging.handlers.SysLogHandler("/dev/log")
handler.setFormatter(logging.Formatter('%(name)s/%(levelname)s: %(message)s'))
logger.addHandler(handler)

GRSF_SYNC = "\xac\xdd\xa4\xe2\xf2\x8c\x20\xfc"
GRSF_SYNC_LENGTH = len(GRSF_SYNC)
GRSF_HEADER_LENGTH = GRSF_SYNC_LENGTH + 1

class UdpSpectrumReceiver(object):

    def __init__(self, port):
        self._udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udpsock.bind(("", port))
        self._workbuf = ""
        self._packet_length = -1
        self._simple_framer_seq_num = None
        self.new_fft_available = Event()
        self.last_fft_received = None
        self.last_fft_received_count = None
        spawn(self._udp_listen_and_segment)

    def _udp_listen_and_segment(self):
        while True:
            self._workbuf += self._udpsock.recv(32768)
            next_packet = -1
            if self._packet_length != -1:
                if len(self._workbuf) >= self._packet_length:
                    if (self._workbuf[
                            self._packet_length - GRSF_HEADER_LENGTH
                            :self._packet_length - GRSF_HEADER_LENGTH + GRSF_SYNC_LENGTH]
                        == GRSF_SYNC):
                        next_packet = self._packet_length
                        logger.debug("header found where expected, packet_length = %i" % (self._packet_length,))
                    else:
                        self._packet_length = -1
                        logger.debug("header NOT found where expected -> will have to relearn packet length")
                else:
                    continue
            if self._packet_length == -1:
                next_packet = self._workbuf.find(GRSF_SYNC) + GRSF_HEADER_LENGTH
                logger.debug("found header at %i" % (next_packet,))
            if next_packet != -1:
                payload = ""
                if self._packet_length != -1:
                    payload = self._workbuf[:next_packet - GRSF_HEADER_LENGTH - 1]
                    # end is minus one because simple framer pads its
                    # payload with one byte, see
                    # gr-digital/include/gnuradio/digital/simple_framer_sync.h
                    next_simple_framer_seq_num_str = self._workbuf[next_packet - GRSF_HEADER_LENGTH + GRSF_SYNC_LENGTH]
                    next_simple_framer_seq_num, = struct.unpack("B", next_simple_framer_seq_num_str)
                    if (self._simple_framer_seq_num != None and
                        (self._simple_framer_seq_num + 1) % 256 != next_simple_framer_seq_num):
                        logger.info("simple_framer_seq_num = %i, next_simple_framer_seq_num = %i" % (
                            self._simple_framer_seq_num, next_simple_framer_seq_num))
                    self._simple_framer_seq_num = next_simple_framer_seq_num
                else:
                    self._packet_length = next_packet
                    logger.debug("learned packet length = %i" % (self._packet_length,))
                self._workbuf = self._workbuf[next_packet:]
                if len(payload) > 0:
                    self.last_fft_received = payload
                    if self.last_fft_received_count == None:
                        self.last_fft_received_count = 0
                    else:
                        self.last_fft_received_count += 1
                    self.new_fft_available.set()
                    self.new_fft_available.clear()

udp_receiver = UdpSpectrumReceiver(6663)

app = Bottle()

def request_id(request):
    return "%s:%s" % (request.environ.get('REMOTE_ADDR'), request.environ.get('REMOTE_PORT'))

@app.route('/spectrum')
def handle_spectrum_ws():
    try:
        logger.info(request_id(request) + ': connection')
        wsock = request.environ.get('wsgi.websocket')
        if not wsock:
            abort(400, request_id(request) + ': Expected WebSocket request.')

        workbuf = ""
        udp_counter = None
        packet_length = -1
        simple_framer_seq_num = None

        while not wsock.closed:
            try:
                while True:
                    udp_receiver.new_fft_available.wait()
                    if udp_counter == None or udp_counter < udp_receiver.last_fft_received_count:
                        udp_counter = udp_receiver.last_fft_received_count
                        wsock.send(udp_receiver.last_fft_received, binary = True)
            except WebSocketError:
                logger.debug(request_id(request) + ": WebSocketError")
                break
        logger.info(request_id(request) + ": websocket closed")
    except Exception, exc:
        logger.error(request_id(request) +
                     ": exception occured in handle_spectrum_ws:\n%s" % (
                format_exc(),))
    finally:
        logger.info(request_id(request) + ": end")

server = WSGIServer(("0.0.0.0", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()
