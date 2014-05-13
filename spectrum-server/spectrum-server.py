from gevent import spawn
from gevent.event import Event
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort
from traceback import format_exc
import gevent.socket as socket, struct, sys, json
from pprint import pformat

GRSF_SYNC = "\xac\xdd\xa4\xe2\xf2\x8c\x20\xfc"
GRSF_SYNC_LENGTH = len(GRSF_SYNC)
GRSF_HEADER_LENGTH = GRSF_SYNC_LENGTH + 1

class UdpSpectrumListener(object):

    def __init__(self, port):
        self._udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udpsock.bind(("", port))
        self.recvd = Event()
        self.last_recv = None
        self.last_recv_counter = None
        spawn(self._udp_fetch)

    def _udp_fetch(self):
        while True:
            self.last_recv = self._udpsock.recv(32768)
            if self.last_recv_counter == None:
                self.last_recv_counter = 0
            else:
                self.last_recv_counter += 1
            self.recvd.set()
            self.recvd.clear()

usl = UdpSpectrumListener(6663)

app = Bottle()

def request_id(request):
    return "%s:%s" % (request.environ.get('REMOTE_ADDR'), request.environ.get('REMOTE_PORT'))

@app.route('/spectrum')
def handle_spectrum_ws():
    try:
        print request_id(request) + ': handle_spectrum_ws start'
        wsock = request.environ.get('wsgi.websocket')
        if not wsock:
            abort(400, request_id(request) + ': Expected WebSocket request.')

        workbuf = ""
        udp_counter = None
        packet_length = -1
        seq_num = None

        while not wsock.closed:
            try:
                while True:
                    usl.recvd.wait()
                    if udp_counter == None or udp_counter < usl.last_recv_counter:
                        udp_counter = usl.last_recv_counter
                        workbuf += usl.last_recv
                        break

                next_packet = -1
                if packet_length != -1:
                    if len(workbuf) >= packet_length:
                        if (workbuf[
                                packet_length - GRSF_HEADER_LENGTH
                                :packet_length - GRSF_HEADER_LENGTH + GRSF_SYNC_LENGTH]
                            == GRSF_SYNC):
                            next_packet = packet_length
                        else:
                            packet_length = -1
                    else:
                        continue
                else:
                    next_packet = workbuf.find(GRSF_SYNC) + GRSF_HEADER_LENGTH
                if next_packet != -1:
                    payload = ""
                    if packet_length != -1:
                        payload = workbuf[:next_packet - GRSF_HEADER_LENGTH - 1]
                        # end is minus one because simple framer pads its
                        # payload with one byte, see
                        # gr-digital/include/gnuradio/digital/simple_framer_sync.h
                        next_seq_num_str = workbuf[next_packet - GRSF_HEADER_LENGTH + GRSF_SYNC_LENGTH]
                        next_seq_num, = struct.unpack("B", next_seq_num_str)
                        if (seq_num != None and
                            (seq_num + 1) % 256 != next_seq_num):
                            print >> sys.stderr, request_id(request) + ": seq_num = %i, next_seq_num = %i" % (
                                seq_num, next_seq_num)
                        seq_num = next_seq_num
                    workbuf = workbuf[next_packet:]
                    packet_length = next_packet
                    if len(payload) > 0:
                        wsock.send(payload, binary = True)
                        payload = ""
            except WebSocketError:
                print request_id(request) + ": WebSocketError"
                break
        print request_id(request) + ": websocket closed"
    except Exception, exc:
        print >> sys.stderr, request_id(request) + ": exception occured in handle_spectrum_ws:\n%s" % (
                format_exc(),)
    finally:
        print request_id(request) + ": handle_spectrum_ws end"

server = WSGIServer(("0.0.0.0", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()
