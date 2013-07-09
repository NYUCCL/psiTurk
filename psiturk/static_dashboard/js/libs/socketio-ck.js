/*! Socket.IO.min.js build:0.9.11, production. Copyright(c) 2011 LearnBoost <dev@learnboost.com> MIT Licensed */var io = "undefined" == typeof module ? {} : module.exports;

(function() {
  (function(e, t) {
    var n = e;
    n.version = "0.9.11", n.protocol = 1, n.transports = [], n.j = [], n.sockets = {}, n.connect = function(e, r) {
      var i = n.util.parseUri(e), s, o;
      t && t.location && (i.protocol = i.protocol || t.location.protocol.slice(0, -1), i.host = i.host || (t.document ? t.document.domain : t.location.hostname), i.port = i.port || t.location.port), s = n.util.uniqueUri(i);
      var u = {
        host: i.host,
        secure: "https" == i.protocol,
        port: i.port || ("https" == i.protocol ? 443 : 80),
        query: i.query || ""
      };
      n.util.merge(u, r);
      if (u["force new connection"] || !n.sockets[s]) o = new n.Socket(u);
      return !u["force new connection"] && o && (n.sockets[s] = o), o = o || n.sockets[s], o.of(i.path.length > 1 ? i.path : "");
    };
  })("object" == typeof module ? module.exports : this.io = {}, this), function(e, t) {
    var n = e.util = {}, r = /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/, i = [ "source", "protocol", "authority", "userInfo", "user", "password", "host", "port", "relative", "path", "directory", "file", "query", "anchor" ];
    n.parseUri = function(e) {
      var t = r.exec(e || ""), n = {}, s = 14;
      while (s--) n[i[s]] = t[s] || "";
      return n;
    }, n.uniqueUri = function(e) {
      var n = e.protocol, r = e.host, i = e.port;
      return "document" in t ? (r = r || document.domain, i = i || (n == "https" && document.location.protocol !== "https:" ? 443 : document.location.port)) : (r = r || "localhost", !i && n == "https" && (i = 443)), (n || "http") + "://" + r + ":" + (i || 80);
    }, n.query = function(e, t) {
      var r = n.chunkQuery(e || ""), i = [];
      n.merge(r, n.chunkQuery(t || ""));
      for (var s in r) r.hasOwnProperty(s) && i.push(s + "=" + r[s]);
      return i.length ? "?" + i.join("&") : "";
    }, n.chunkQuery = function(e) {
      var t = {}, n = e.split("&"), r = 0, i = n.length, s;
      for (; r < i; ++r) s = n[r].split("="), s[0] && (t[s[0]] = s[1]);
      return t;
    };
    var s = !1;
    n.load = function(e) {
      if ("document" in t && document.readyState === "complete" || s) return e();
      n.on(t, "load", e, !1);
    }, n.on = function(e, t, n, r) {
      e.attachEvent ? e.attachEvent("on" + t, n) : e.addEventListener && e.addEventListener(t, n, r);
    }, n.request = function(e) {
      if (e && "undefined" != typeof XDomainRequest && !n.ua.hasCORS) return new XDomainRequest;
      if ("undefined" != typeof XMLHttpRequest && (!e || n.ua.hasCORS)) return new XMLHttpRequest;
      if (!e) try {
        return new (window[[ "Active" ].concat("Object").join("X")])("Microsoft.XMLHTTP");
      } catch (t) {}
      return null;
    }, "undefined" != typeof window && n.load(function() {
      s = !0;
    }), n.defer = function(e) {
      if (!n.ua.webkit || "undefined" != typeof importScripts) return e();
      n.load(function() {
        setTimeout(e, 100);
      });
    }, n.merge = function(e, t, r, i) {
      var s = i || [], o = typeof r == "undefined" ? 2 : r, u;
      for (u in t) t.hasOwnProperty(u) && n.indexOf(s, u) < 0 && (typeof e[u] != "object" || !o ? (e[u] = t[u], s.push(t[u])) : n.merge(e[u], t[u], o - 1, s));
      return e;
    }, n.mixin = function(e, t) {
      n.merge(e.prototype, t.prototype);
    }, n.inherit = function(e, t) {
      function n() {}
      n.prototype = t.prototype, e.prototype = new n;
    }, n.isArray = Array.isArray || function(e) {
      return Object.prototype.toString.call(e) === "[object Array]";
    }, n.intersect = function(e, t) {
      var r = [], i = e.length > t.length ? e : t, s = e.length > t.length ? t : e;
      for (var o = 0, u = s.length; o < u; o++) ~n.indexOf(i, s[o]) && r.push(s[o]);
      return r;
    }, n.indexOf = function(e, t, n) {
      for (var r = e.length, n = n < 0 ? n + r < 0 ? 0 : n + r : n || 0; n < r && e[n] !== t; n++) ;
      return r <= n ? -1 : n;
    }, n.toArray = function(e) {
      var t = [];
      for (var n = 0, r = e.length; n < r; n++) t.push(e[n]);
      return t;
    }, n.ua = {}, n.ua.hasCORS = "undefined" != typeof XMLHttpRequest && function() {
      try {
        var e = new XMLHttpRequest;
      } catch (t) {
        return !1;
      }
      return e.withCredentials != undefined;
    }(), n.ua.webkit = "undefined" != typeof navigator && /webkit/i.test(navigator.userAgent), n.ua.iDevice = "undefined" != typeof navigator && /iPad|iPhone|iPod/i.test(navigator.userAgent);
  }("undefined" != typeof io ? io : module.exports, this), function(e, t) {
    function n() {}
    e.EventEmitter = n, n.prototype.on = function(e, n) {
      return this.$events || (this.$events = {}), this.$events[e] ? t.util.isArray(this.$events[e]) ? this.$events[e].push(n) : this.$events[e] = [ this.$events[e], n ] : this.$events[e] = n, this;
    }, n.prototype.addListener = n.prototype.on, n.prototype.once = function(e, t) {
      function n() {
        r.removeListener(e, n), t.apply(this, arguments);
      }
      var r = this;
      return n.listener = t, this.on(e, n), this;
    }, n.prototype.removeListener = function(e, n) {
      if (this.$events && this.$events[e]) {
        var r = this.$events[e];
        if (t.util.isArray(r)) {
          var i = -1;
          for (var s = 0, o = r.length; s < o; s++) if (r[s] === n || r[s].listener && r[s].listener === n) {
            i = s;
            break;
          }
          if (i < 0) return this;
          r.splice(i, 1), r.length || delete this.$events[e];
        } else (r === n || r.listener && r.listener === n) && delete this.$events[e];
      }
      return this;
    }, n.prototype.removeAllListeners = function(e) {
      return e === undefined ? (this.$events = {}, this) : (this.$events && this.$events[e] && (this.$events[e] = null), this);
    }, n.prototype.listeners = function(e) {
      return this.$events || (this.$events = {}), this.$events[e] || (this.$events[e] = []), t.util.isArray(this.$events[e]) || (this.$events[e] = [ this.$events[e] ]), this.$events[e];
    }, n.prototype.emit = function(e) {
      if (!this.$events) return !1;
      var n = this.$events[e];
      if (!n) return !1;
      var r = Array.prototype.slice.call(arguments, 1);
      if ("function" == typeof n) n.apply(this, r); else {
        if (!t.util.isArray(n)) return !1;
        var i = n.slice();
        for (var s = 0, o = i.length; s < o; s++) i[s].apply(this, r);
      }
      return !0;
    };
  }("undefined" != typeof io ? io : module.exports, "undefined" != typeof io ? io : module.parent.exports), function(exports, nativeJSON) {
    function f(e) {
      return e < 10 ? "0" + e : e;
    }
    function date(e, t) {
      return isFinite(e.valueOf()) ? e.getUTCFullYear() + "-" + f(e.getUTCMonth() + 1) + "-" + f(e.getUTCDate()) + "T" + f(e.getUTCHours()) + ":" + f(e.getUTCMinutes()) + ":" + f(e.getUTCSeconds()) + "Z" : null;
    }
    function quote(e) {
      return escapable.lastIndex = 0, escapable.test(e) ? '"' + e.replace(escapable, function(e) {
        var t = meta[e];
        return typeof t == "string" ? t : "\\u" + ("0000" + e.charCodeAt(0).toString(16)).slice(-4);
      }) + '"' : '"' + e + '"';
    }
    function str(e, t) {
      var n, r, i, s, o = gap, u, a = t[e];
      a instanceof Date && (a = date(e)), typeof rep == "function" && (a = rep.call(t, e, a));
      switch (typeof a) {
       case "string":
        return quote(a);
       case "number":
        return isFinite(a) ? String(a) : "null";
       case "boolean":
       case "null":
        return String(a);
       case "object":
        if (!a) return "null";
        gap += indent, u = [];
        if (Object.prototype.toString.apply(a) === "[object Array]") {
          s = a.length;
          for (n = 0; n < s; n += 1) u[n] = str(n, a) || "null";
          return i = u.length === 0 ? "[]" : gap ? "[\n" + gap + u.join(",\n" + gap) + "\n" + o + "]" : "[" + u.join(",") + "]", gap = o, i;
        }
        if (rep && typeof rep == "object") {
          s = rep.length;
          for (n = 0; n < s; n += 1) typeof rep[n] == "string" && (r = rep[n], i = str(r, a), i && u.push(quote(r) + (gap ? ": " : ":") + i));
        } else for (r in a) Object.prototype.hasOwnProperty.call(a, r) && (i = str(r, a), i && u.push(quote(r) + (gap ? ": " : ":") + i));
        return i = u.length === 0 ? "{}" : gap ? "{\n" + gap + u.join(",\n" + gap) + "\n" + o + "}" : "{" + u.join(",") + "}", gap = o, i;
      }
    }
    "use strict";
    if (nativeJSON && nativeJSON.parse) return exports.JSON = {
      parse: nativeJSON.parse,
      stringify: nativeJSON.stringify
    };
    var JSON = exports.JSON = {}, cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g, escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g, gap, indent, meta = {
      "\b": "\\b",
      "	": "\\t",
      "\n": "\\n",
      "\f": "\\f",
      "\r": "\\r",
      '"': '\\"',
      "\\": "\\\\"
    }, rep;
    JSON.stringify = function(e, t, n) {
      var r;
      gap = "", indent = "";
      if (typeof n == "number") for (r = 0; r < n; r += 1) indent += " "; else typeof n == "string" && (indent = n);
      rep = t;
      if (!t || typeof t == "function" || typeof t == "object" && typeof t.length == "number") return str("", {
        "": e
      });
      throw new Error("JSON.stringify");
    }, JSON.parse = function(text, reviver) {
      function walk(e, t) {
        var n, r, i = e[t];
        if (i && typeof i == "object") for (n in i) Object.prototype.hasOwnProperty.call(i, n) && (r = walk(i, n), r !== undefined ? i[n] = r : delete i[n]);
        return reviver.call(e, t, i);
      }
      var j;
      text = String(text), cx.lastIndex = 0, cx.test(text) && (text = text.replace(cx, function(e) {
        return "\\u" + ("0000" + e.charCodeAt(0).toString(16)).slice(-4);
      }));
      if (/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, "@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, "]").replace(/(?:^|:|,)(?:\s*\[)+/g, ""))) return j = eval("(" + text + ")"), typeof reviver == "function" ? walk({
        "": j
      }, "") : j;
      throw new SyntaxError("JSON.parse");
    };
  }("undefined" != typeof io ? io : module.exports, typeof JSON != "undefined" ? JSON : undefined), function(e, t) {
    var n = e.parser = {}, r = n.packets = [ "disconnect", "connect", "heartbeat", "message", "json", "event", "ack", "error", "noop" ], i = n.reasons = [ "transport not supported", "client not handshaken", "unauthorized" ], s = n.advice = [ "reconnect" ], o = t.JSON, u = t.util.indexOf;
    n.encodePacket = function(e) {
      var t = u(r, e.type), n = e.id || "", a = e.endpoint || "", l = e.ack, c = null;
      switch (e.type) {
       case "error":
        var p = e.reason ? u(i, e.reason) : "", v = e.advice ? u(s, e.advice) : "";
        if (p !== "" || v !== "") c = p + (v !== "" ? "+" + v : "");
        break;
       case "message":
        e.data !== "" && (c = e.data);
        break;
       case "event":
        var m = {
          name: e.name
        };
        e.args && e.args.length && (m.args = e.args), c = o.stringify(m);
        break;
       case "json":
        c = o.stringify(e.data);
        break;
       case "connect":
        e.qs && (c = e.qs);
        break;
       case "ack":
        c = e.ackId + (e.args && e.args.length ? "+" + o.stringify(e.args) : "");
      }
      var y = [ t, n + (l == "data" ? "+" : ""), a ];
      return c !== null && c !== undefined && y.push(c), y.join(":");
    }, n.encodePayload = function(e) {
      var t = "";
      if (e.length == 1) return e[0];
      for (var n = 0, r = e.length; n < r; n++) {
        var i = e[n];
        t += "�" + i.length + "�" + e[n];
      }
      return t;
    };
    var a = /([^:]+):([0-9]+)?(\+)?:([^:]+)?:?([\s\S]*)?/;
    n.decodePacket = function(e) {
      var t = e.match(a);
      if (!t) return {};
      var n = t[2] || "", e = t[5] || "", u = {
        type: r[t[1]],
        endpoint: t[4] || ""
      };
      n && (u.id = n, t[3] ? u.ack = "data" : u.ack = !0);
      switch (u.type) {
       case "error":
        var t = e.split("+");
        u.reason = i[t[0]] || "", u.advice = s[t[1]] || "";
        break;
       case "message":
        u.data = e || "";
        break;
       case "event":
        try {
          var l = o.parse(e);
          u.name = l.name, u.args = l.args;
        } catch (c) {}
        u.args = u.args || [];
        break;
       case "json":
        try {
          u.data = o.parse(e);
        } catch (c) {}
        break;
       case "connect":
        u.qs = e || "";
        break;
       case "ack":
        var t = e.match(/^([0-9]+)(\+)?(.*)/);
        if (t) {
          u.ackId = t[1], u.args = [];
          if (t[3]) try {
            u.args = t[3] ? o.parse(t[3]) : [];
          } catch (c) {}
        }
        break;
       case "disconnect":
       case "heartbeat":
      }
      return u;
    }, n.decodePayload = function(e) {
      if (e.charAt(0) == "�") {
        var t = [];
        for (var r = 1, i = ""; r < e.length; r++) e.charAt(r) == "�" ? (t.push(n.decodePacket(e.substr(r + 1).substr(0, i))), r += Number(i) + 1, i = "") : i += e.charAt(r);
        return t;
      }
      return [ n.decodePacket(e) ];
    };
  }("undefined" != typeof io ? io : module.exports, "undefined" != typeof io ? io : module.parent.exports), function(e, t) {
    function n(e, t) {
      this.socket = e, this.sessid = t;
    }
    e.Transport = n, t.util.mixin(n, t.EventEmitter), n.prototype.heartbeats = function() {
      return !0;
    }, n.prototype.onData = function(e) {
      this.clearCloseTimeout(), (this.socket.connected || this.socket.connecting || this.socket.reconnecting) && this.setCloseTimeout();
      if (e !== "") {
        var n = t.parser.decodePayload(e);
        if (n && n.length) for (var r = 0, i = n.length; r < i; r++) this.onPacket(n[r]);
      }
      return this;
    }, n.prototype.onPacket = function(e) {
      return this.socket.setHeartbeatTimeout(), e.type == "heartbeat" ? this.onHeartbeat() : (e.type == "connect" && e.endpoint == "" && this.onConnect(), e.type == "error" && e.advice == "reconnect" && (this.isOpen = !1), this.socket.onPacket(e), this);
    }, n.prototype.setCloseTimeout = function() {
      if (!this.closeTimeout) {
        var e = this;
        this.closeTimeout = setTimeout(function() {
          e.onDisconnect();
        }, this.socket.closeTimeout);
      }
    }, n.prototype.onDisconnect = function() {
      return this.isOpen && this.close(), this.clearTimeouts(), this.socket.onDisconnect(), this;
    }, n.prototype.onConnect = function() {
      return this.socket.onConnect(), this;
    }, n.prototype.clearCloseTimeout = function() {
      this.closeTimeout && (clearTimeout(this.closeTimeout), this.closeTimeout = null);
    }, n.prototype.clearTimeouts = function() {
      this.clearCloseTimeout(), this.reopenTimeout && clearTimeout(this.reopenTimeout);
    }, n.prototype.packet = function(e) {
      this.send(t.parser.encodePacket(e));
    }, n.prototype.onHeartbeat = function(e) {
      this.packet({
        type: "heartbeat"
      });
    }, n.prototype.onOpen = function() {
      this.isOpen = !0, this.clearCloseTimeout(), this.socket.onOpen();
    }, n.prototype.onClose = function() {
      var e = this;
      this.isOpen = !1, this.socket.onClose(), this.onDisconnect();
    }, n.prototype.prepareUrl = function() {
      var e = this.socket.options;
      return this.scheme() + "://" + e.host + ":" + e.port + "/" + e.resource + "/" + t.protocol + "/" + this.name + "/" + this.sessid;
    }, n.prototype.ready = function(e, t) {
      t.call(this);
    };
  }("undefined" != typeof io ? io : module.exports, "undefined" != typeof io ? io : module.parent.exports), function(e, t, n) {
    function r(e) {
      this.options = {
        port: 80,
        secure: !1,
        document: "document" in n ? document : !1,
        resource: "socket.io",
        transports: t.transports,
        "connect timeout": 1e4,
        "try multiple transports": !0,
        reconnect: !0,
        "reconnection delay": 500,
        "reconnection limit": Infinity,
        "reopen delay": 3e3,
        "max reconnection attempts": 10,
        "sync disconnect on unload": !1,
        "auto connect": !0,
        "flash policy port": 10843,
        manualFlush: !1
      }, t.util.merge(this.options, e), this.connected = !1, this.open = !1, this.connecting = !1, this.reconnecting = !1, this.namespaces = {}, this.buffer = [], this.doBuffer = !1;
      if (this.options["sync disconnect on unload"] && (!this.isXDomain() || t.util.ua.hasCORS)) {
        var r = this;
        t.util.on(n, "beforeunload", function() {
          r.disconnectSync();
        }, !1);
      }
      this.options["auto connect"] && this.connect();
    }
    function i() {}
    e.Socket = r, t.util.mixin(r, t.EventEmitter), r.prototype.of = function(e) {
      return this.namespaces[e] || (this.namespaces[e] = new t.SocketNamespace(this, e), e !== "" && this.namespaces[e].packet({
        type: "connect"
      })), this.namespaces[e];
    }, r.prototype.publish = function() {
      this.emit.apply(this, arguments);
      var e;
      for (var t in this.namespaces) this.namespaces.hasOwnProperty(t) && (e = this.of(t), e.$emit.apply(e, arguments));
    }, r.prototype.handshake = function(e) {
      function n(t) {
        t instanceof Error ? (r.connecting = !1, r.onError(t.message)) : e.apply(null, t.split(":"));
      }
      var r = this, s = this.options, o = [ "http" + (s.secure ? "s" : "") + ":/", s.host + ":" + s.port, s.resource, t.protocol, t.util.query(this.options.query, "t=" + +(new Date)) ].join("/");
      if (this.isXDomain() && !t.util.ua.hasCORS) {
        var u = document.getElementsByTagName("script")[0], a = document.createElement("script");
        a.src = o + "&jsonp=" + t.j.length, u.parentNode.insertBefore(a, u), t.j.push(function(e) {
          n(e), a.parentNode.removeChild(a);
        });
      } else {
        var f = t.util.request();
        f.open("GET", o, !0), this.isXDomain() && (f.withCredentials = !0), f.onreadystatechange = function() {
          f.readyState == 4 && (f.onreadystatechange = i, f.status == 200 ? n(f.responseText) : f.status == 403 ? r.onError(f.responseText) : (r.connecting = !1, !r.reconnecting && r.onError(f.responseText)));
        }, f.send(null);
      }
    }, r.prototype.getTransport = function(e) {
      var n = e || this.transports, r;
      for (var i = 0, s; s = n[i]; i++) if (t.Transport[s] && t.Transport[s].check(this) && (!this.isXDomain() || t.Transport[s].xdomainCheck(this))) return new t.Transport[s](this, this.sessionid);
      return null;
    }, r.prototype.connect = function(e) {
      if (this.connecting) return this;
      var n = this;
      return n.connecting = !0, this.handshake(function(r, i, s, o) {
        function u(e) {
          n.transport && n.transport.clearTimeouts(), n.transport = n.getTransport(e);
          if (!n.transport) return n.publish("connect_failed");
          n.transport.ready(n, function() {
            n.connecting = !0, n.publish("connecting", n.transport.name), n.transport.open(), n.options["connect timeout"] && (n.connectTimeoutTimer = setTimeout(function() {
              if (!n.connected) {
                n.connecting = !1;
                if (n.options["try multiple transports"]) {
                  var e = n.transports;
                  while (e.length > 0 && e.splice(0, 1)[0] != n.transport.name) ;
                  e.length ? u(e) : n.publish("connect_failed");
                }
              }
            }, n.options["connect timeout"]));
          });
        }
        n.sessionid = r, n.closeTimeout = s * 1e3, n.heartbeatTimeout = i * 1e3, n.transports || (n.transports = n.origTransports = o ? t.util.intersect(o.split(","), n.options.transports) : n.options.transports), n.setHeartbeatTimeout(), u(n.transports), n.once("connect", function() {
          clearTimeout(n.connectTimeoutTimer), e && typeof e == "function" && e();
        });
      }), this;
    }, r.prototype.setHeartbeatTimeout = function() {
      clearTimeout(this.heartbeatTimeoutTimer);
      if (this.transport && !this.transport.heartbeats()) return;
      var e = this;
      this.heartbeatTimeoutTimer = setTimeout(function() {
        e.transport.onClose();
      }, this.heartbeatTimeout);
    }, r.prototype.packet = function(e) {
      return this.connected && !this.doBuffer ? this.transport.packet(e) : this.buffer.push(e), this;
    }, r.prototype.setBuffer = function(e) {
      this.doBuffer = e, !e && this.connected && this.buffer.length && (this.options.manualFlush || this.flushBuffer());
    }, r.prototype.flushBuffer = function() {
      this.transport.payload(this.buffer), this.buffer = [];
    }, r.prototype.disconnect = function() {
      if (this.connected || this.connecting) this.open && this.of("").packet({
        type: "disconnect"
      }), this.onDisconnect("booted");
      return this;
    }, r.prototype.disconnectSync = function() {
      var e = t.util.request(), n = [ "http" + (this.options.secure ? "s" : "") + ":/", this.options.host + ":" + this.options.port, this.options.resource, t.protocol, "", this.sessionid ].join("/") + "/?disconnect=1";
      e.open("GET", n, !1), e.send(null), this.onDisconnect("booted");
    }, r.prototype.isXDomain = function() {
      var e = n.location.port || ("https:" == n.location.protocol ? 443 : 80);
      return this.options.host !== n.location.hostname || this.options.port != e;
    }, r.prototype.onConnect = function() {
      this.connected || (this.connected = !0, this.connecting = !1, this.doBuffer || this.setBuffer(!1), this.emit("connect"));
    }, r.prototype.onOpen = function() {
      this.open = !0;
    }, r.prototype.onClose = function() {
      this.open = !1, clearTimeout(this.heartbeatTimeoutTimer);
    }, r.prototype.onPacket = function(e) {
      this.of(e.endpoint).onPacket(e);
    }, r.prototype.onError = function(e) {
      e && e.advice && e.advice === "reconnect" && (this.connected || this.connecting) && (this.disconnect(), this.options.reconnect && this.reconnect()), this.publish("error", e && e.reason ? e.reason : e);
    }, r.prototype.onDisconnect = function(e) {
      var t = this.connected, n = this.connecting;
      this.connected = !1, this.connecting = !1, this.open = !1;
      if (t || n) this.transport.close(), this.transport.clearTimeouts(), t && (this.publish("disconnect", e), "booted" != e && this.options.reconnect && !this.reconnecting && this.reconnect());
    }, r.prototype.reconnect = function() {
      function e() {
        if (n.connected) {
          for (var e in n.namespaces) n.namespaces.hasOwnProperty(e) && "" !== e && n.namespaces[e].packet({
            type: "connect"
          });
          n.publish("reconnect", n.transport.name, n.reconnectionAttempts);
        }
        clearTimeout(n.reconnectionTimer), n.removeListener("connect_failed", t), n.removeListener("connect", t), n.reconnecting = !1, delete n.reconnectionAttempts, delete n.reconnectionDelay, delete n.reconnectionTimer, delete n.redoTransports, n.options["try multiple transports"] = i;
      }
      function t() {
        if (!n.reconnecting) return;
        if (n.connected) return e();
        if (n.connecting && n.reconnecting) return n.reconnectionTimer = setTimeout(t, 1e3);
        n.reconnectionAttempts++ >= r ? n.redoTransports ? (n.publish("reconnect_failed"), e()) : (n.on("connect_failed", t), n.options["try multiple transports"] = !0, n.transports = n.origTransports, n.transport = n.getTransport(), n.redoTransports = !0, n.connect()) : (n.reconnectionDelay < s && (n.reconnectionDelay *= 2), n.connect(), n.publish("reconnecting", n.reconnectionDelay, n.reconnectionAttempts), n.reconnectionTimer = setTimeout(t, n.reconnectionDelay));
      }
      this.reconnecting = !0, this.reconnectionAttempts = 0, this.reconnectionDelay = this.options["reconnection delay"];
      var n = this, r = this.options["max reconnection attempts"], i = this.options["try multiple transports"], s = this.options["reconnection limit"];
      this.options["try multiple transports"] = !1, this.reconnectionTimer = setTimeout(t, this.reconnectionDelay), this.on("connect", t);
    };
  }("undefined" != typeof io ? io : module.exports, "undefined" != typeof io ? io : module.parent.exports, this), function(e, t) {
    function n(e, t) {
      this.socket = e, this.name = t || "", this.flags = {}, this.json = new r(this, "json"), this.ackPackets = 0, this.acks = {};
    }
    function r(e, t) {
      this.namespace = e, this.name = t;
    }
    e.SocketNamespace = n, t.util.mixin(n, t.EventEmitter), n.prototype.$emit = t.EventEmitter.prototype.emit, n.prototype.of = function() {
      return this.socket.of.apply(this.socket, arguments);
    }, n.prototype.packet = function(e) {
      return e.endpoint = this.name, this.socket.packet(e), this.flags = {}, this;
    }, n.prototype.send = function(e, t) {
      var n = {
        type: this.flags.json ? "json" : "message",
        data: e
      };
      return "function" == typeof t && (n.id = ++this.ackPackets, n.ack = !0, this.acks[n.id] = t), this.packet(n);
    }, n.prototype.emit = function(e) {
      var t = Array.prototype.slice.call(arguments, 1), n = t[t.length - 1], r = {
        type: "event",
        name: e
      };
      return "function" == typeof n && (r.id = ++this.ackPackets, r.ack = "data", this.acks[r.id] = n, t = t.slice(0, t.length - 1)), r.args = t, this.packet(r);
    }, n.prototype.disconnect = function() {
      return this.name === "" ? this.socket.disconnect() : (this.packet({
        type: "disconnect"
      }), this.$emit("disconnect")), this;
    }, n.prototype.onPacket = function(e) {
      function n() {
        r.packet({
          type: "ack",
          args: t.util.toArray(arguments),
          ackId: e.id
        });
      }
      var r = this;
      switch (e.type) {
       case "connect":
        this.$emit("connect");
        break;
       case "disconnect":
        this.name === "" ? this.socket.onDisconnect(e.reason || "booted") : this.$emit("disconnect", e.reason);
        break;
       case "message":
       case "json":
        var i = [ "message", e.data ];
        e.ack == "data" ? i.push(n) : e.ack && this.packet({
          type: "ack",
          ackId: e.id
        }), this.$emit.apply(this, i);
        break;
       case "event":
        var i = [ e.name ].concat(e.args);
        e.ack == "data" && i.push(n), this.$emit.apply(this, i);
        break;
       case "ack":
        this.acks[e.ackId] && (this.acks[e.ackId].apply(this, e.args), delete this.acks[e.ackId]);
        break;
       case "error":
        e.advice ? this.socket.onError(e) : e.reason == "unauthorized" ? this.$emit("connect_failed", e.reason) : this.$emit("error", e.reason);
      }
    }, r.prototype.send = function() {
      this.namespace.flags[this.name] = !0, this.namespace.send.apply(this.namespace, arguments);
    }, r.prototype.emit = function() {
      this.namespace.flags[this.name] = !0, this.namespace.emit.apply(this.namespace, arguments);
    };
  }("undefined" != typeof io ? io : module.exports, "undefined" != typeof io ? io : module.parent.exports), function(e, t, n) {
    function r(e) {
      t.Transport.apply(this, arguments);
    }
    e.websocket = r, t.util.inherit(r, t.Transport), r.prototype.name = "websocket", r.prototype.open = function() {
      var e = t.util.query(this.socket.options.query), r = this, i;
      return i || (i = n.MozWebSocket || n.WebSocket), this.websocket = new i(this.prepareUrl() + e), this.websocket.onopen = function() {
        r.onOpen(), r.socket.setBuffer(!1);
      }, this.websocket.onmessage = function(e) {
        r.onData(e.data);
      }, this.websocket.onclose = function() {
        r.onClose(), r.socket.setBuffer(!0);
      }, this.websocket.onerror = function(e) {
        r.onError(e);
      }, this;
    }, t.util.ua.iDevice ? r.prototype.send = function(e) {
      var t = this;
      return setTimeout(function() {
        t.websocket.send(e);
      }, 0), this;
    } : r.prototype.send = function(e) {
      return this.websocket.send(e), this;
    }, r.prototype.payload = function(e) {
      for (var t = 0, n = e.length; t < n; t++) this.packet(e[t]);
      return this;
    }, r.prototype.close = function() {
      return this.websocket.close(), this;
    }, r.prototype.onError = function(e) {
      this.socket.onError(e);
    }, r.prototype.scheme = function() {
      return this.socket.options.secure ? "wss" : "ws";
    }, r.check = function() {
      return "WebSocket" in n && !("__addTask" in WebSocket) || "MozWebSocket" in n;
    }, r.xdomainCheck = function() {
      return !0;
    }, t.transports.push("websocket");
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports, this), function(e, t) {
    function n() {
      t.Transport.websocket.apply(this, arguments);
    }
    e.flashsocket = n, t.util.inherit(n, t.Transport.websocket), n.prototype.name = "flashsocket", n.prototype.open = function() {
      var e = this, n = arguments;
      return WebSocket.__addTask(function() {
        t.Transport.websocket.prototype.open.apply(e, n);
      }), this;
    }, n.prototype.send = function() {
      var e = this, n = arguments;
      return WebSocket.__addTask(function() {
        t.Transport.websocket.prototype.send.apply(e, n);
      }), this;
    }, n.prototype.close = function() {
      return WebSocket.__tasks.length = 0, t.Transport.websocket.prototype.close.call(this), this;
    }, n.prototype.ready = function(e, r) {
      function i() {
        var t = e.options, i = t["flash policy port"], o = [ "http" + (t.secure ? "s" : "") + ":/", t.host + ":" + t.port, t.resource, "static/flashsocket", "WebSocketMain" + (e.isXDomain() ? "Insecure" : "") + ".swf" ];
        n.loaded || (typeof WEB_SOCKET_SWF_LOCATION == "undefined" && (WEB_SOCKET_SWF_LOCATION = o.join("/")), i !== 843 && WebSocket.loadFlashPolicyFile("xmlsocket://" + t.host + ":" + i), WebSocket.__initialize(), n.loaded = !0), r.call(s);
      }
      var s = this;
      if (document.body) return i();
      t.util.load(i);
    }, n.check = function() {
      return typeof WebSocket != "undefined" && "__initialize" in WebSocket && !!swfobject ? swfobject.getFlashPlayerVersion().major >= 10 : !1;
    }, n.xdomainCheck = function() {
      return !0;
    }, typeof window != "undefined" && (WEB_SOCKET_DISABLE_AUTO_INITIALIZATION = !0), t.transports.push("flashsocket");
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports);
  if ("undefined" != typeof window) var swfobject = function() {
    function e() {
      if (R) return;
      try {
        var e = O.getElementsByTagName("body")[0].appendChild(m("span"));
        e.parentNode.removeChild(e);
      } catch (t) {
        return;
      }
      R = !0;
      var n = D.length;
      for (var r = 0; r < n; r++) D[r]();
    }
    function t(e) {
      R ? e() : D[D.length] = e;
    }
    function n(e) {
      if (typeof A.addEventListener != S) A.addEventListener("load", e, !1); else if (typeof O.addEventListener != S) O.addEventListener("load", e, !1); else if (typeof A.attachEvent != S) g(A, "onload", e); else if (typeof A.onload == "function") {
        var t = A.onload;
        A.onload = function() {
          t(), e();
        };
      } else A.onload = e;
    }
    function r() {
      _ ? i() : s();
    }
    function i() {
      var e = O.getElementsByTagName("body")[0], t = m(x);
      t.setAttribute("type", C);
      var n = e.appendChild(t);
      if (n) {
        var r = 0;
        (function() {
          if (typeof n.GetVariable != S) {
            var i = n.GetVariable("$version");
            i && (i = i.split(" ")[1].split(","), V.pv = [ parseInt(i[0], 10), parseInt(i[1], 10), parseInt(i[2], 10) ]);
          } else if (r < 10) {
            r++, setTimeout(arguments.callee, 10);
            return;
          }
          e.removeChild(t), n = null, s();
        })();
      } else s();
    }
    function s() {
      var e = P.length;
      if (e > 0) for (var t = 0; t < e; t++) {
        var n = P[t].id, r = P[t].callbackFn, i = {
          success: !1,
          id: n
        };
        if (V.pv[0] > 0) {
          var s = v(n);
          if (s) if (y(P[t].swfVersion) && !(V.wk && V.wk < 312)) w(n, !0), r && (i.success = !0, i.ref = o(n), r(i)); else if (P[t].expressInstall && u()) {
            var l = {};
            l.data = P[t].expressInstall, l.width = s.getAttribute("width") || "0", l.height = s.getAttribute("height") || "0", s.getAttribute("class") && (l.styleclass = s.getAttribute("class")), s.getAttribute("align") && (l.align = s.getAttribute("align"));
            var c = {}, h = s.getElementsByTagName("param"), p = h.length;
            for (var d = 0; d < p; d++) h[d].getAttribute("name").toLowerCase() != "movie" && (c[h[d].getAttribute("name")] = h[d].getAttribute("value"));
            a(l, c, n, r);
          } else f(s), r && r(i);
        } else {
          w(n, !0);
          if (r) {
            var m = o(n);
            m && typeof m.SetVariable != S && (i.success = !0, i.ref = m), r(i);
          }
        }
      }
    }
    function o(e) {
      var t = null, n = v(e);
      if (n && n.nodeName == "OBJECT") if (typeof n.SetVariable != S) t = n; else {
        var r = n.getElementsByTagName(x)[0];
        r && (t = r);
      }
      return t;
    }
    function u() {
      return !U && y("6.0.65") && (V.win || V.mac) && !(V.wk && V.wk < 312);
    }
    function a(e, t, n, r) {
      U = !0, I = r || null, q = {
        success: !1,
        id: n
      };
      var i = v(n);
      if (i) {
        i.nodeName == "OBJECT" ? (j = l(i), F = null) : (j = i, F = n), e.id = k;
        if (typeof e.width == S || !/%$/.test(e.width) && parseInt(e.width, 10) < 310) e.width = "310";
        if (typeof e.height == S || !/%$/.test(e.height) && parseInt(e.height, 10) < 137) e.height = "137";
        O.title = O.title.slice(0, 47) + " - Flash Player Installation";
        var s = V.ie && V.win ? [ "Active" ].concat("").join("X") : "PlugIn", o = "MMredirectURL=" + A.location.toString().replace(/&/g, "%26") + "&MMplayerType=" + s + "&MMdoctitle=" + O.title;
        typeof t.flashvars != S ? t.flashvars += "&" + o : t.flashvars = o;
        if (V.ie && V.win && i.readyState != 4) {
          var u = m("div");
          n += "SWFObjectNew", u.setAttribute("id", n), i.parentNode.insertBefore(u, i), i.style.display = "none", function() {
            i.readyState == 4 ? i.parentNode.removeChild(i) : setTimeout(arguments.callee, 10);
          }();
        }
        c(e, t, n);
      }
    }
    function f(e) {
      if (V.ie && V.win && e.readyState != 4) {
        var t = m("div");
        e.parentNode.insertBefore(t, e), t.parentNode.replaceChild(l(e), t), e.style.display = "none", function() {
          e.readyState == 4 ? e.parentNode.removeChild(e) : setTimeout(arguments.callee, 10);
        }();
      } else e.parentNode.replaceChild(l(e), e);
    }
    function l(e) {
      var t = m("div");
      if (V.win && V.ie) t.innerHTML = e.innerHTML; else {
        var n = e.getElementsByTagName(x)[0];
        if (n) {
          var r = n.childNodes;
          if (r) {
            var i = r.length;
            for (var s = 0; s < i; s++) (r[s].nodeType != 1 || r[s].nodeName != "PARAM") && r[s].nodeType != 8 && t.appendChild(r[s].cloneNode(!0));
          }
        }
      }
      return t;
    }
    function c(e, t, n) {
      var r, i = v(n);
      if (V.wk && V.wk < 312) return r;
      if (i) {
        typeof e.id == S && (e.id = n);
        if (V.ie && V.win) {
          var s = "";
          for (var o in e) e[o] != Object.prototype[o] && (o.toLowerCase() == "data" ? t.movie = e[o] : o.toLowerCase() == "styleclass" ? s += ' class="' + e[o] + '"' : o.toLowerCase() != "classid" && (s += " " + o + '="' + e[o] + '"'));
          var u = "";
          for (var a in t) t[a] != Object.prototype[a] && (u += '<param name="' + a + '" value="' + t[a] + '" />');
          i.outerHTML = '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"' + s + ">" + u + "</object>", H[H.length] = e.id, r = v(e.id);
        } else {
          var f = m(x);
          f.setAttribute("type", C);
          for (var l in e) e[l] != Object.prototype[l] && (l.toLowerCase() == "styleclass" ? f.setAttribute("class", e[l]) : l.toLowerCase() != "classid" && f.setAttribute(l, e[l]));
          for (var c in t) t[c] != Object.prototype[c] && c.toLowerCase() != "movie" && h(f, c, t[c]);
          i.parentNode.replaceChild(f, i), r = f;
        }
      }
      return r;
    }
    function h(e, t, n) {
      var r = m("param");
      r.setAttribute("name", t), r.setAttribute("value", n), e.appendChild(r);
    }
    function p(e) {
      var t = v(e);
      t && t.nodeName == "OBJECT" && (V.ie && V.win ? (t.style.display = "none", function() {
        t.readyState == 4 ? d(e) : setTimeout(arguments.callee, 10);
      }()) : t.parentNode.removeChild(t));
    }
    function d(e) {
      var t = v(e);
      if (t) {
        for (var n in t) typeof t[n] == "function" && (t[n] = null);
        t.parentNode.removeChild(t);
      }
    }
    function v(e) {
      var t = null;
      try {
        t = O.getElementById(e);
      } catch (n) {}
      return t;
    }
    function m(e) {
      return O.createElement(e);
    }
    function g(e, t, n) {
      e.attachEvent(t, n), B[B.length] = [ e, t, n ];
    }
    function y(e) {
      var t = V.pv, n = e.split(".");
      return n[0] = parseInt(n[0], 10), n[1] = parseInt(n[1], 10) || 0, n[2] = parseInt(n[2], 10) || 0, t[0] > n[0] || t[0] == n[0] && t[1] > n[1] || t[0] == n[0] && t[1] == n[1] && t[2] >= n[2] ? !0 : !1;
    }
    function b(e, t, n, r) {
      if (V.ie && V.mac) return;
      var i = O.getElementsByTagName("head")[0];
      if (!i) return;
      var s = n && typeof n == "string" ? n : "screen";
      r && (z = null, W = null);
      if (!z || W != s) {
        var o = m("style");
        o.setAttribute("type", "text/css"), o.setAttribute("media", s), z = i.appendChild(o), V.ie && V.win && typeof O.styleSheets != S && O.styleSheets.length > 0 && (z = O.styleSheets[O.styleSheets.length - 1]), W = s;
      }
      V.ie && V.win ? z && typeof z.addRule == x && z.addRule(e, t) : z && typeof O.createTextNode != S && z.appendChild(O.createTextNode(e + " {" + t + "}"));
    }
    function w(e, t) {
      if (!X) return;
      var n = t ? "visible" : "hidden";
      R && v(e) ? v(e).style.visibility = n : b("#" + e, "visibility:" + n);
    }
    function E(e) {
      var t = /[\\\"<>\.;]/, n = t.exec(e) != null;
      return n && typeof encodeURIComponent != S ? encodeURIComponent(e) : e;
    }
    var S = "undefined", x = "object", T = "Shockwave Flash", N = "ShockwaveFlash.ShockwaveFlash", C = "application/x-shockwave-flash", k = "SWFObjectExprInst", L = "onreadystatechange", A = window, O = document, M = navigator, _ = !1, D = [ r ], P = [], H = [], B = [], j, F, I, q, R = !1, U = !1, z, W, X = !0, V = function() {
      var e = typeof O.getElementById != S && typeof O.getElementsByTagName != S && typeof O.createElement != S, t = M.userAgent.toLowerCase(), n = M.platform.toLowerCase(), r = n ? /win/.test(n) : /win/.test(t), i = n ? /mac/.test(n) : /mac/.test(t), s = /webkit/.test(t) ? parseFloat(t.replace(/^.*webkit\/(\d+(\.\d+)?).*$/, "$1")) : !1, o = !1, u = [ 0, 0, 0 ], a = null;
      if (typeof M.plugins != S && typeof M.plugins[T] == x) a = M.plugins[T].description, a && (typeof M.mimeTypes == S || !M.mimeTypes[C] || !!M.mimeTypes[C].enabledPlugin) && (_ = !0, o = !1, a = a.replace(/^.*\s+(\S+\s+\S+$)/, "$1"), u[0] = parseInt(a.replace(/^(.*)\..*$/, "$1"), 10), u[1] = parseInt(a.replace(/^.*\.(.*)\s.*$/, "$1"), 10), u[2] = /[a-zA-Z]/.test(a) ? parseInt(a.replace(/^.*[a-zA-Z]+(.*)$/, "$1"), 10) : 0); else if (typeof A[[ "Active" ].concat("Object").join("X")] != S) try {
        var f = new (window[[ "Active" ].concat("Object").join("X")])(N);
        f && (a = f.GetVariable("$version"), a && (o = !0, a = a.split(" ")[1].split(","), u = [ parseInt(a[0], 10), parseInt(a[1], 10), parseInt(a[2], 10) ]));
      } catch (l) {}
      return {
        w3: e,
        pv: u,
        wk: s,
        ie: o,
        win: r,
        mac: i
      };
    }(), $ = function() {
      if (!V.w3) return;
      (typeof O.readyState != S && O.readyState == "complete" || typeof O.readyState == S && (O.getElementsByTagName("body")[0] || O.body)) && e(), R || (typeof O.addEventListener != S && O.addEventListener("DOMContentLoaded", e, !1), V.ie && V.win && (O.attachEvent(L, function() {
        O.readyState == "complete" && (O.detachEvent(L, arguments.callee), e());
      }), A == top && function() {
        if (R) return;
        try {
          O.documentElement.doScroll("left");
        } catch (t) {
          setTimeout(arguments.callee, 0);
          return;
        }
        e();
      }()), V.wk && function() {
        if (R) return;
        if (!/loaded|complete/.test(O.readyState)) {
          setTimeout(arguments.callee, 0);
          return;
        }
        e();
      }(), n(e));
    }(), J = function() {
      V.ie && V.win && window.attachEvent("onunload", function() {
        var e = B.length;
        for (var t = 0; t < e; t++) B[t][0].detachEvent(B[t][1], B[t][2]);
        var n = H.length;
        for (var r = 0; r < n; r++) p(H[r]);
        for (var i in V) V[i] = null;
        V = null;
        for (var s in swfobject) swfobject[s] = null;
        swfobject = null;
      });
    }();
    return {
      registerObject: function(e, t, n, r) {
        if (V.w3 && e && t) {
          var i = {};
          i.id = e, i.swfVersion = t, i.expressInstall = n, i.callbackFn = r, P[P.length] = i, w(e, !1);
        } else r && r({
          success: !1,
          id: e
        });
      },
      getObjectById: function(e) {
        if (V.w3) return o(e);
      },
      embedSWF: function(e, n, r, i, s, o, f, l, h, p) {
        var d = {
          success: !1,
          id: n
        };
        V.w3 && !(V.wk && V.wk < 312) && e && n && r && i && s ? (w(n, !1), t(function() {
          r += "", i += "";
          var t = {};
          if (h && typeof h === x) for (var v in h) t[v] = h[v];
          t.data = e, t.width = r, t.height = i;
          var m = {};
          if (l && typeof l === x) for (var g in l) m[g] = l[g];
          if (f && typeof f === x) for (var b in f) typeof m.flashvars != S ? m.flashvars += "&" + b + "=" + f[b] : m.flashvars = b + "=" + f[b];
          if (y(s)) {
            var E = c(t, m, n);
            t.id == n && w(n, !0), d.success = !0, d.ref = E;
          } else {
            if (o && u()) {
              t.data = o, a(t, m, n, p);
              return;
            }
            w(n, !0);
          }
          p && p(d);
        })) : p && p(d);
      },
      switchOffAutoHideShow: function() {
        X = !1;
      },
      ua: V,
      getFlashPlayerVersion: function() {
        return {
          major: V.pv[0],
          minor: V.pv[1],
          release: V.pv[2]
        };
      },
      hasFlashPlayerVersion: y,
      createSWF: function(e, t, n) {
        return V.w3 ? c(e, t, n) : undefined;
      },
      showExpressInstall: function(e, t, n, r) {
        V.w3 && u() && a(e, t, n, r);
      },
      removeSWF: function(e) {
        V.w3 && p(e);
      },
      createCSS: function(e, t, n, r) {
        V.w3 && b(e, t, n, r);
      },
      addDomLoadEvent: t,
      addLoadEvent: n,
      getQueryParamValue: function(e) {
        var t = O.location.search || O.location.hash;
        if (t) {
          /\?/.test(t) && (t = t.split("?")[1]);
          if (e == null) return E(t);
          var n = t.split("&");
          for (var r = 0; r < n.length; r++) if (n[r].substring(0, n[r].indexOf("=")) == e) return E(n[r].substring(n[r].indexOf("=") + 1));
        }
        return "";
      },
      expressInstallCallback: function() {
        if (U) {
          var e = v(k);
          e && j && (e.parentNode.replaceChild(j, e), F && (w(F, !0), V.ie && V.win && (j.style.display = "block")), I && I(q)), U = !1;
        }
      }
    };
  }();
  (function() {
    if ("undefined" == typeof window || window.WebSocket) return;
    var e = window.console;
    if (!e || !e.log || !e.error) e = {
      log: function() {},
      error: function() {}
    };
    if (!swfobject.hasFlashPlayerVersion("10.0.0")) {
      e.error("Flash Player >= 10.0.0 is required.");
      return;
    }
    location.protocol == "file:" && e.error("WARNING: web-socket-js doesn't work in file:///... URL unless you set Flash Security Settings properly. Open the page via Web server i.e. http://..."), WebSocket = function(e, t, n, r, i) {
      var s = this;
      s.__id = WebSocket.__nextId++, WebSocket.__instances[s.__id] = s, s.readyState = WebSocket.CONNECTING, s.bufferedAmount = 0, s.__events = {}, t ? typeof t == "string" && (t = [ t ]) : t = [], setTimeout(function() {
        WebSocket.__addTask(function() {
          WebSocket.__flash.create(s.__id, e, t, n || null, r || 0, i || null);
        });
      }, 0);
    }, WebSocket.prototype.send = function(e) {
      if (this.readyState == WebSocket.CONNECTING) throw "INVALID_STATE_ERR: Web Socket connection has not been established";
      var t = WebSocket.__flash.send(this.__id, encodeURIComponent(e));
      return t < 0 ? !0 : (this.bufferedAmount += t, !1);
    }, WebSocket.prototype.close = function() {
      if (this.readyState == WebSocket.CLOSED || this.readyState == WebSocket.CLOSING) return;
      this.readyState = WebSocket.CLOSING, WebSocket.__flash.close(this.__id);
    }, WebSocket.prototype.addEventListener = function(e, t, n) {
      e in this.__events || (this.__events[e] = []), this.__events[e].push(t);
    }, WebSocket.prototype.removeEventListener = function(e, t, n) {
      if (!(e in this.__events)) return;
      var r = this.__events[e];
      for (var i = r.length - 1; i >= 0; --i) if (r[i] === t) {
        r.splice(i, 1);
        break;
      }
    }, WebSocket.prototype.dispatchEvent = function(e) {
      var t = this.__events[e.type] || [];
      for (var n = 0; n < t.length; ++n) t[n](e);
      var r = this["on" + e.type];
      r && r(e);
    }, WebSocket.prototype.__handleEvent = function(e) {
      "readyState" in e && (this.readyState = e.readyState), "protocol" in e && (this.protocol = e.protocol);
      var t;
      if (e.type == "open" || e.type == "error") t = this.__createSimpleEvent(e.type); else if (e.type == "close") t = this.__createSimpleEvent("close"); else {
        if (e.type != "message") throw "unknown event type: " + e.type;
        var n = decodeURIComponent(e.message);
        t = this.__createMessageEvent("message", n);
      }
      this.dispatchEvent(t);
    }, WebSocket.prototype.__createSimpleEvent = function(e) {
      if (document.createEvent && window.Event) {
        var t = document.createEvent("Event");
        return t.initEvent(e, !1, !1), t;
      }
      return {
        type: e,
        bubbles: !1,
        cancelable: !1
      };
    }, WebSocket.prototype.__createMessageEvent = function(e, t) {
      if (document.createEvent && window.MessageEvent && !window.opera) {
        var n = document.createEvent("MessageEvent");
        return n.initMessageEvent("message", !1, !1, t, null, null, window, null), n;
      }
      return {
        type: e,
        data: t,
        bubbles: !1,
        cancelable: !1
      };
    }, WebSocket.CONNECTING = 0, WebSocket.OPEN = 1, WebSocket.CLOSING = 2, WebSocket.CLOSED = 3, WebSocket.__flash = null, WebSocket.__instances = {}, WebSocket.__tasks = [], WebSocket.__nextId = 0, WebSocket.loadFlashPolicyFile = function(e) {
      WebSocket.__addTask(function() {
        WebSocket.__flash.loadManualPolicyFile(e);
      });
    }, WebSocket.__initialize = function() {
      if (WebSocket.__flash) return;
      WebSocket.__swfLocation && (window.WEB_SOCKET_SWF_LOCATION = WebSocket.__swfLocation);
      if (!window.WEB_SOCKET_SWF_LOCATION) {
        e.error("[WebSocket] set WEB_SOCKET_SWF_LOCATION to location of WebSocketMain.swf");
        return;
      }
      var t = document.createElement("div");
      t.id = "webSocketContainer", t.style.position = "absolute", WebSocket.__isFlashLite() ? (t.style.left = "0px", t.style.top = "0px") : (t.style.left = "-100px", t.style.top = "-100px");
      var n = document.createElement("div");
      n.id = "webSocketFlash", t.appendChild(n), document.body.appendChild(t), swfobject.embedSWF(WEB_SOCKET_SWF_LOCATION, "webSocketFlash", "1", "1", "10.0.0", null, null, {
        hasPriority: !0,
        swliveconnect: !0,
        allowScriptAccess: "always"
      }, null, function(t) {
        t.success || e.error("[WebSocket] swfobject.embedSWF failed");
      });
    }, WebSocket.__onFlashInitialized = function() {
      setTimeout(function() {
        WebSocket.__flash = document.getElementById("webSocketFlash"), WebSocket.__flash.setCallerUrl(location.href), WebSocket.__flash.setDebug(!!window.WEB_SOCKET_DEBUG);
        for (var e = 0; e < WebSocket.__tasks.length; ++e) WebSocket.__tasks[e]();
        WebSocket.__tasks = [];
      }, 0);
    }, WebSocket.__onFlashEvent = function() {
      return setTimeout(function() {
        try {
          var t = WebSocket.__flash.receiveEvents();
          for (var n = 0; n < t.length; ++n) WebSocket.__instances[t[n].webSocketId].__handleEvent(t[n]);
        } catch (r) {
          e.error(r);
        }
      }, 0), !0;
    }, WebSocket.__log = function(t) {
      e.log(decodeURIComponent(t));
    }, WebSocket.__error = function(t) {
      e.error(decodeURIComponent(t));
    }, WebSocket.__addTask = function(e) {
      WebSocket.__flash ? e() : WebSocket.__tasks.push(e);
    }, WebSocket.__isFlashLite = function() {
      if (!window.navigator || !window.navigator.mimeTypes) return !1;
      var e = window.navigator.mimeTypes["application/x-shockwave-flash"];
      return !e || !e.enabledPlugin || !e.enabledPlugin.filename ? !1 : e.enabledPlugin.filename.match(/flashlite/i) ? !0 : !1;
    }, window.WEB_SOCKET_DISABLE_AUTO_INITIALIZATION || (window.addEventListener ? window.addEventListener("load", function() {
      WebSocket.__initialize();
    }, !1) : window.attachEvent("onload", function() {
      WebSocket.__initialize();
    }));
  })(), function(e, t, n) {
    function r(e) {
      if (!e) return;
      t.Transport.apply(this, arguments), this.sendBuffer = [];
    }
    function i() {}
    e.XHR = r, t.util.inherit(r, t.Transport), r.prototype.open = function() {
      return this.socket.setBuffer(!1), this.onOpen(), this.get(), this.setCloseTimeout(), this;
    }, r.prototype.payload = function(e) {
      var n = [];
      for (var r = 0, i = e.length; r < i; r++) n.push(t.parser.encodePacket(e[r]));
      this.send(t.parser.encodePayload(n));
    }, r.prototype.send = function(e) {
      return this.post(e), this;
    }, r.prototype.post = function(e) {
      function t() {
        this.readyState == 4 && (this.onreadystatechange = i, s.posting = !1, this.status == 200 ? s.socket.setBuffer(!1) : s.onClose());
      }
      function r() {
        this.onload = i, s.socket.setBuffer(!1);
      }
      var s = this;
      this.socket.setBuffer(!0), this.sendXHR = this.request("POST"), n.XDomainRequest && this.sendXHR instanceof XDomainRequest ? this.sendXHR.onload = this.sendXHR.onerror = r : this.sendXHR.onreadystatechange = t, this.sendXHR.send(e);
    }, r.prototype.close = function() {
      return this.onClose(), this;
    }, r.prototype.request = function(e) {
      var n = t.util.request(this.socket.isXDomain()), r = t.util.query(this.socket.options.query, "t=" + +(new Date));
      n.open(e || "GET", this.prepareUrl() + r, !0);
      if (e == "POST") try {
        n.setRequestHeader ? n.setRequestHeader("Content-type", "text/plain;charset=UTF-8") : n.contentType = "text/plain";
      } catch (i) {}
      return n;
    }, r.prototype.scheme = function() {
      return this.socket.options.secure ? "https" : "http";
    }, r.check = function(e, r) {
      try {
        var i = t.util.request(r), s = n.XDomainRequest && i instanceof XDomainRequest, o = e && e.options && e.options.secure ? "https:" : "http:", u = n.location && o != n.location.protocol;
        if (i && (!s || !u)) return !0;
      } catch (a) {}
      return !1;
    }, r.xdomainCheck = function(e) {
      return r.check(e, !0);
    };
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports, this), function(e, t) {
    function n(e) {
      t.Transport.XHR.apply(this, arguments);
    }
    e.htmlfile = n, t.util.inherit(n, t.Transport.XHR), n.prototype.name = "htmlfile", n.prototype.get = function() {
      this.doc = new (window[[ "Active" ].concat("Object").join("X")])("htmlfile"), this.doc.open(), this.doc.write("<html></html>"), this.doc.close(), this.doc.parentWindow.s = this;
      var e = this.doc.createElement("div");
      e.className = "socketio", this.doc.body.appendChild(e), this.iframe = this.doc.createElement("iframe"), e.appendChild(this.iframe);
      var n = this, r = t.util.query(this.socket.options.query, "t=" + +(new Date));
      this.iframe.src = this.prepareUrl() + r, t.util.on(window, "unload", function() {
        n.destroy();
      });
    }, n.prototype._ = function(e, t) {
      this.onData(e);
      try {
        var n = t.getElementsByTagName("script")[0];
        n.parentNode.removeChild(n);
      } catch (r) {}
    }, n.prototype.destroy = function() {
      if (this.iframe) {
        try {
          this.iframe.src = "about:blank";
        } catch (e) {}
        this.doc = null, this.iframe.parentNode.removeChild(this.iframe), this.iframe = null, CollectGarbage();
      }
    }, n.prototype.close = function() {
      return this.destroy(), t.Transport.XHR.prototype.close.call(this);
    }, n.check = function(e) {
      if (typeof window != "undefined" && [ "Active" ].concat("Object").join("X") in window) try {
        var n = new (window[[ "Active" ].concat("Object").join("X")])("htmlfile");
        return n && t.Transport.XHR.check(e);
      } catch (r) {}
      return !1;
    }, n.xdomainCheck = function() {
      return !1;
    }, t.transports.push("htmlfile");
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports), function(e, t, n) {
    function r() {
      t.Transport.XHR.apply(this, arguments);
    }
    function i() {}
    e["xhr-polling"] = r, t.util.inherit(r, t.Transport.XHR), t.util.merge(r, t.Transport.XHR), r.prototype.name = "xhr-polling", r.prototype.heartbeats = function() {
      return !1;
    }, r.prototype.open = function() {
      var e = this;
      return t.Transport.XHR.prototype.open.call(e), !1;
    }, r.prototype.get = function() {
      function e() {
        this.readyState == 4 && (this.onreadystatechange = i, this.status == 200 ? (s.onData(this.responseText), s.get()) : s.onClose());
      }
      function t() {
        this.onload = i, this.onerror = i, s.retryCounter = 1, s.onData(this.responseText), s.get();
      }
      function r() {
        s.retryCounter++, !s.retryCounter || s.retryCounter > 3 ? s.onClose() : s.get();
      }
      if (!this.isOpen) return;
      var s = this;
      this.xhr = this.request(), n.XDomainRequest && this.xhr instanceof XDomainRequest ? (this.xhr.onload = t, this.xhr.onerror = r) : this.xhr.onreadystatechange = e, this.xhr.send(null);
    }, r.prototype.onClose = function() {
      t.Transport.XHR.prototype.onClose.call(this);
      if (this.xhr) {
        this.xhr.onreadystatechange = this.xhr.onload = this.xhr.onerror = i;
        try {
          this.xhr.abort();
        } catch (e) {}
        this.xhr = null;
      }
    }, r.prototype.ready = function(e, n) {
      var r = this;
      t.util.defer(function() {
        n.call(r);
      });
    }, t.transports.push("xhr-polling");
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports, this), function(e, t, n) {
    function r(e) {
      t.Transport["xhr-polling"].apply(this, arguments), this.index = t.j.length;
      var n = this;
      t.j.push(function(e) {
        n._(e);
      });
    }
    var i = n.document && "MozAppearance" in n.document.documentElement.style;
    e["jsonp-polling"] = r, t.util.inherit(r, t.Transport["xhr-polling"]), r.prototype.name = "jsonp-polling", r.prototype.post = function(e) {
      function n() {
        r(), i.socket.setBuffer(!1);
      }
      function r() {
        i.iframe && i.form.removeChild(i.iframe);
        try {
          f = document.createElement('<iframe name="' + i.iframeId + '">');
        } catch (e) {
          f = document.createElement("iframe"), f.name = i.iframeId;
        }
        f.id = i.iframeId, i.form.appendChild(f), i.iframe = f;
      }
      var i = this, s = t.util.query(this.socket.options.query, "t=" + +(new Date) + "&i=" + this.index);
      if (!this.form) {
        var o = document.createElement("form"), u = document.createElement("textarea"), a = this.iframeId = "socketio_iframe_" + this.index, f;
        o.className = "socketio", o.style.position = "absolute", o.style.top = "0px", o.style.left = "0px", o.style.display = "none", o.target = a, o.method = "POST", o.setAttribute("accept-charset", "utf-8"), u.name = "d", o.appendChild(u), document.body.appendChild(o), this.form = o, this.area = u;
      }
      this.form.action = this.prepareUrl() + s, r(), this.area.value = t.JSON.stringify(e);
      try {
        this.form.submit();
      } catch (l) {}
      this.iframe.attachEvent ? f.onreadystatechange = function() {
        i.iframe.readyState == "complete" && n();
      } : this.iframe.onload = n, this.socket.setBuffer(!0);
    }, r.prototype.get = function() {
      var e = this, n = document.createElement("script"), r = t.util.query(this.socket.options.query, "t=" + +(new Date) + "&i=" + this.index);
      this.script && (this.script.parentNode.removeChild(this.script), this.script = null), n.async = !0, n.src = this.prepareUrl() + r, n.onerror = function() {
        e.onClose();
      };
      var s = document.getElementsByTagName("script")[0];
      s.parentNode.insertBefore(n, s), this.script = n, i && setTimeout(function() {
        var e = document.createElement("iframe");
        document.body.appendChild(e), document.body.removeChild(e);
      }, 100);
    }, r.prototype._ = function(e) {
      return this.onData(e), this.isOpen && this.get(), this;
    }, r.prototype.ready = function(e, n) {
      var r = this;
      if (!i) return n.call(this);
      t.util.load(function() {
        n.call(r);
      });
    }, r.check = function() {
      return "document" in n;
    }, r.xdomainCheck = function() {
      return !0;
    }, t.transports.push("jsonp-polling");
  }("undefined" != typeof io ? io.Transport : module.exports, "undefined" != typeof io ? io : module.parent.exports, this), typeof define == "function" && define.amd && define([], function() {
    return io;
  });
})();