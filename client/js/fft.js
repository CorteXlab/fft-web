function Fft(elem, host, port, udpport, rearrange_halves, mean_window_size) {
    this._host = host;
    this._port = port;
    this._udpport = udpport;
    this._rearrange_halves = rearrange_halves;
    this._mean_window_size = mean_window_size;
    this._mean_window = [];
    this._elem = d3.select(elem);
    this._total_width = $(elem).width();
    this._total_height = $(elem).height();
    this._margin = {top: 20, right: 20, bottom: 30, left: 50};
    this._graph_width = this._total_width
        - this._margin.left - this._margin.right;
    this._graph_height = this._total_height
        - this._margin.top - this._margin.bottom;
    this._chart = this._elem.append("svg")
        .attr("width", this._total_width)
        .attr("height", this._total_height)
        .append("g")
        .attr("transform", "translate(" + this._margin.left + "," + this._margin.top + ")");
    this._current_fft_size = -1;
    this._sx = null;
    this._sy = d3.scale.linear()
        .domain([-128,127])
        .rangeRound([0, this._graph_height]);
    this._yaxis = d3.svg.axis()
        .scale(this._sy)
        .tickValues([])
        .tickFormat(function(d) { return (((d+128.0) / 256.0) * -100.0).toFixed(0); })
        .orient("left");
    this._svgxaxis = this._chart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this._graph_height + ")");
    this._svgyaxis = this._chart.append("g")
        .attr("class", "y axis")
        .call(this._yaxis);
    this._fftline = d3.svg.line()
        .x(function(d, i) { return this._sx(i); })
        .y(function(d) { return this._graph_height - this._sy(d); });
    this._fftpath = this._chart.append("svg:path")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", "1.5px");
    return this;
}

Fft.prototype._push_data = function(data) {
    this._mean_window.push(data);
    while (this._mean_window.length > this._mean_window_size) {
        this._mean_window.shift();
    }
}

Fft.prototype._get_window_mean = function() {
    var min_size = -1;
    for (var i = 0; i < this._mean_window.length; i++) {
        if (min_size == -1 || this._mean_window[i].length < min_size) {
            min_size = this._mean_window[i].length;
        }
    }
    mean = new Int8Array(min_size);
    for (var x = 0; x < min_size; x++) {
        var m = 0.0;
        for (var i = 0; i < this._mean_window.length; i++) {
            m = m + this._mean_window[i][x];
        }
        mean[x] = m / this._mean_window.length;
    }
    return mean;
}

Fft.prototype._update_sx = function(size) {
    if (size != this._current_fft_size) {
        this._sx = d3.scale.linear()
            .domain([0, size])
            .rangeRound([0, this._graph_width]);
        this._xaxis = d3.svg.axis()
            .scale(this._sx)
            .tickValues([0, size/2, size])
            .tickFormat(function(d) { return d - size/2; })
            .orient("bottom");
        this._svgxaxis.call(this._xaxis);
        this._current_fft_size = size;
    }
}

function get_rearranged_fft(fft) {
    var rearranged = new Int8Array(fft.length);
    middle = Math.floor(fft.length / 2);
    rearranged.set(fft.subarray(middle, fft.length), 0);
    rearranged.set(fft.subarray(0, middle), middle);
    return rearranged;
}

Fft.prototype.start = function() {
    this._ws = new WebSocket("ws://" + this._host + ":" + this._port + "/fftws/" + this._udpport);
    this._ws.binaryType = "arraybuffer";
    this._ws.onopen = function() { console.log("fft websocket opened"); };
    this._ws.onclose = function() { console.log("fft websocket closed"); };
    var self = this;
    this._ws.onmessage = function(evt) {
        if (evt.data instanceof ArrayBuffer) {
            fft = new Int8Array(evt.data);
            self._push_data(fft);
            mean = self._get_window_mean();
            if (self._rearrange_halves) {
                mean = get_rearranged_fft(mean);
            }
            self._update_sx(mean.length);
            self._fftpath.attr("d", self._fftline(mean));
        }
    };
}

Fft.prototype.stop = function() {
    this._ws.close();
}
