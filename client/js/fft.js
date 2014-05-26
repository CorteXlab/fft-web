function Fft(elem, host, port, udpport) {
    this._host = host;
    this._port = port;
    this._udpport = udpport;
    this._elem = d3.select(elem);
    this._width = $(elem).width();
    this._height = $(elem).height();
    this._chart = this._elem.append("svg")
        .attr("width", this._width)
        .attr("height", this._height);
    this._sx = null;
    this._current_fft_size = -1;
    this._sy = d3.scale.pow()
        .exponent(4)
        .domain([0, 255])
        .rangeRound([0, this._height]);
    this._fftline = d3.svg.line()
        .x(function(d, i) { return this._sx(i); })
        .y(function(d) { return this._height - this._sy(d); });
    this._fftpath = this._chart.append("svg:path")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", "1.5px");
    return this;
}

Fft.prototype._update_sx = function(size) {
    if (size != this._current_fft_size) {
        this._sx = d3.scale.linear()
            .domain([0, size])
            .rangeRound([0, this._width]);
        this._current_fft_size = size;
    }
}

Fft.prototype.start = function() {
    this._ws = new WebSocket("ws://" + this._host + ":" + this._port + "/fft/" + this._udpport);
    this._ws.binaryType = "arraybuffer";
    this._ws.onopen = function() { console.log("fft websocket opened"); };
    this._ws.onclose = function() { console.log("fft websocket closed"); };
    var self = this;
    this._ws.onmessage = function(evt) {
        if (evt.data instanceof ArrayBuffer) {
            fft = new Uint8Array(evt.data);
            self._update_sx(fft.length);
            self._fftpath.attr("d", self._fftline(fft));
        }
    };
}

Fft.prototype.stop = function() {
    this._ws.close();
}
