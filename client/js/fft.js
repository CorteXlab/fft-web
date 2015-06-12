function formatn(n) {
    if (Math.abs(n) < 1e-3 || Math.abs(n) > 1e4) {
        return parseFloat(n.toPrecision(3)).toExponential();
    } else {
        return n.toPrecision(3);
    }
}

function Fft(elem, host, port, udpport, rearrange_halves, mean_window_size, x_axis_min, x_axis_max, y_axis_min, y_axis_max) {
    this._host = host;
    this._port = port;
    this._udpport = udpport;
    this._rearrange_halves = rearrange_halves;
    this._mean_window_size = mean_window_size;
    this._mean_window = [];
    this._x_min = undefined;
    this._x_max = undefined;
    this._x_axis_min = x_axis_min;
    this._x_axis_max = x_axis_max;
    this._y_min = undefined;
    this._y_max = undefined;
    this._y_axis_min = y_axis_min;
    this._y_axis_max = y_axis_max;
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
    this._svgxaxis = this._chart.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + this._graph_height + ")");
    this._svgyaxis = this._chart.append("g")
        .attr("class", "axis");
    this._update_x_range(0,1024);
    this._update_y_range(-128, 127);
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

Fft.prototype._update_x_range = function(x_min, x_max) {
    if (x_min != this._x_min || x_max != this._x_max) {
        this._x_min = x_min;
        this._x_max = x_max;
        this._sx = d3.scale.linear()
            .domain([x_min, x_max])
            .rangeRound([0, this._graph_width]);
        this.x_axis(this._x_axis_min, this._x_axis_max);
    }
}

Fft.prototype.x_axis = function(x_axis_min, x_axis_max) {
    this._x_axis_min = x_axis_min;
    this._x_axis_max = x_axis_max;
    this._xaxis = d3.svg.axis()
        .scale(this._sx)
        .orient("bottom")
        .tickValues([]);
    if (this._x_axis_max - this._x_axis_min > 0 && this._x_max - this._x_min > 0) {
        a = (this._x_axis_min - this._x_axis_max) / (this._x_min - this._x_max);
        b = (this._x_axis_max * this._x_min - this._x_axis_min * this._x_max) / (this._x_min - this._x_max);
        this._xaxis.tickValues([this._x_min, (this._x_max - this._x_min)/2, this._x_max])
            .tickFormat(function(d) { return formatn(a * d + b); });
    }
    this._svgxaxis.call(this._xaxis);
}

Fft.prototype._update_y_range = function(y_min, y_max) {
    if (y_min != this._y_min || y_max != this._y_max) {
        this._y_min = y_min;
        this._y_max = y_max;
        this._sy = d3.scale.linear()
            .domain([y_min, y_max])
            .rangeRound([0, this._graph_height]);
        this.y_axis(this._y_axis_min, this._y_axis_max);
    }
}

Fft.prototype.y_axis = function(y_axis_min, y_axis_max) {
    this._y_axis_min = y_axis_min;
    this._y_axis_max = y_axis_max;
    this._yaxis = d3.svg.axis()
        .scale(this._sy)
        .orient("left")
        .tickValues([]);
    if (this._y_axis_max - this._y_axis_min > 0 && this._y_max - this._y_min > 0) {
        a = (this._y_axis_max - this._y_axis_min) / (this._y_min - this._y_max);
        b = (this._y_axis_min * this._y_min - this._y_axis_max * this._y_max) / (this._y_min - this._y_max);
        this._yaxis.tickValues([this._y_min, (this._y_max - this._y_min)/2, this._y_max])
            .tickFormat(function(d) { return formatn(a * d + b); });
    }
    this._svgyaxis.call(this._yaxis);
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
            self._update_x_range(0, mean.length);
            self._fftpath.attr("d", self._fftline(mean));
        }
    };
    this._keepalive = setInterval(function() {
        self._ws.send("ping");
    }, 60000);
}

Fft.prototype.stop = function() {
    clearInterval(this._keepalive);
    this._ws.close();
}

Fft.prototype.clear = function() {
    this._fftpath.attr("d", null);
}
