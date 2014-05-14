fft-web
=======

- a GNURadio block which sends a signal FFT by UDP to...

- a websocket server (python / bottle / gevent-websocket) which packs
  and broadcasts this FFT data to websockets, which can be opened by...

- html/javascript code (relying on d3js) for real-time display of the
  fft in web-browsers.
