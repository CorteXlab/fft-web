import sys, os
import_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/..")
if not import_path in sys.path: sys.path.insert(1, import_path)
from fft_server import app as application
