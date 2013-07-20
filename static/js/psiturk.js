/*
 * Requires:
 *     jquery
 *     backbone
 *     underscore
 */


/****************
 * Internals    *
 ***************/

// Sets up global notifications pub/sub
// Notifications get submitted here (via trigger) and subscribed to (via on)
Backbone.Notifications = {};
_.extend(Backbone.Notifications, Backbone.Events);

var optoutmessage = "By leaving this page, you opt out of the experiment.";
var startTask = function () {
	psiTurk.saveData();
	
	$.ajax("inexp", {
			type: "POST",
			async: true,
			data: {uniqueId: uniqueId}
	});
	
	// Provide opt-out 
	$(window).on("beforeunload", function(){
		psiTurk.saveData();
		
		$.ajax("quitter", {
				type: "POST",
				async: false,
				data: {uniqueId: uniqueId}
		});
		alert(msg);
		return "Are you sure you want to leave the experiment?";
	});
};
Backbone.Notifications.on('_psiturk_finishedinstructions', startTask);
Backbone.Notifications.on('_psiturk_finishedtask', function(msg) { $(window).off("beforeunload"); });

$(window).blur( function() {
	Backbone.Notifications.trigger('_psiturk_lostfocus');
});

$(window).focus( function() {
	Backbone.Notifications.trigger('_psiturk_gainedfocus');	
});



// track changes in window size
triggerResize = function() {
	Backbone.Notifications.trigger('_psiturk_windowresize', [window.innerWidth, window.innerHeight]);
};

var to = false;
$(window).resize(function(){
 if(to !== false)
    clearTimeout(to);
 to = setTimeout(triggerResize, 200);
});



/****************
 * HTML PAGES   *
 ***************/

var Page = Backbone.Model.extend({
	defaults: {
		name: "",
		html: ""
	}
});

var PageCollection = Backbone.Collection.extend({
	model: Page,
	url: '/pages',
	
	// need this because Flask won't return JSON with
	// array at the top level
	parse: function(response) {
		return response.collection;
	},
	
	getHTML: function(pagename, callback) {
		matches = this.where({name: pagename});
		if (matches.length > 0) callback(matches[0].get('html'));
		else console.log("Page not found: ", pagename);
	}
});


/****************
 * IMAGES       *
 ***************/

var ExpImage = Backbone.Model.extend({
	defaults: {
		name: "",
		loc: "",
		el: null
	},
	initialize: function() {
		var img = new Image();
		img.src = this.get('loc');
		this.set('el', img);
	}
});

var ImageCollection = Backbone.Collection.extend({
	
	model: ExpImage,
	url: '/images',

	parse: function(response) {
		return response.collection;
	},

	getImage: function(imagename, callback) {
		matches = this.where({name: imagename});
		if (matches.length > 0) {
			callback(matches[0].get('el'));
		} else {
			console.log('Image not found: ', imagename);
		}
	}
});


/****************
 * TASK DATA    *
 ***************/

var TaskData = Backbone.Model.extend({
	urlRoot: "/sync", // Save will PUT to /data, with mimetype 'application/JSON'
	id: uniqueId,
	
	defaults: {
		condition: 0,
		counterbalance: 0,
		assignmentId: 0,
		workerId: 0,
		hitId: 0,
		currenttrial: 0,
		bonus: 0,
		data: "",
		questiondata: {},
		eventdata: [],
		useragent: ""
	},
	
	initialize: function() {
		this.useragent = navigator.userAgent;
		this.addEvent('initialized', null);
		this.addEvent('window_resize', [window.innerWidth, window.innerHeight]);

		this.listenTo(Backbone.Notifications, '_psiturk_lostfocus', function() { this.addEvent('focus', 'off'); });
		this.listenTo(Backbone.Notifications, '_psiturk_gainedfocus', function() { this.addEvent('focus', 'on'); });
		this.listenTo(Backbone.Notifications, '_psiturk_windowresize', function(newsize) { this.addEvent('window_resize', newsize); });
	},

	addTrialData: function(trialdata) {
		trialdata = [this.id, this.get("currenttrial"), (new Date().getTime())].concat(trialdata);
		this.set({"data": this.get("data").concat(trialdata, "\n")});
		this.set({"currenttrial": this.get("currenttrial")+1});
	},
	
	addUnstructuredData: function(field, response) {
		qd = this.get("questiondata");
		qd[field] = response;
		this.set("questiondata", qd);
	},

	addEvent: function(eventtype, value) {
		var interval,
		    ed = this.get('eventdata'),
		    timestamp = new Date().getTime();

		if (eventtype == 'initialized') {
			interval = 0;
		} else {
			interval = timestamp - ed[ed.length-1]['timestamp'];
		}

		ed.push({'eventtype': eventtype, 'value': value, 'timestamp': timestamp, 'interval': interval});
		this.set('eventdata', ed);
	}
});



/*******
 * API *
 ******/
var PsiTurk = function() {
	var taskdata = new TaskData();
	taskdata.fetch({async: false});
	
	// Load pages and images:
	var pages = new PageCollection();
	pages.fetch({async: false});
	
	var images = new ImageCollection();
	images.fetch({async: false});
	
	/*  DATA: */
	this.pages = pages;
	this.images = images;
	this.taskdata = taskdata;
	
	/*  METHODS: */
	// Get HTML file from collection and pass on to a callback
	this.getPage = function(pagename, callback) {
		pages.getHTML(pagename, callback);
	};
	
	// Get a single image element and pass to callback
	this.getImage = function(imagename, callback) {
		images.getImage(imagename, callback);
	};
	
	// Add a line of data with any number of columns
	this.recordTrialData = function(trialdata) {
		taskdata.addTrialData(trialdata);
	};
	
	// Add data value for a named column. If a value already
	// exists for that column, it will be overwritten
	this.recordUnstructuredData = function(field, value) {
		taskdata.addUnstructuredData(field, value);
	};
	
	// Save data to server
	this.saveData = function(callbacks) {
		taskdata.save(undefined, callbacks);
	};
	
	// Notify app that participant has begun main experiment
	this.finishInstructions = function(optmessage) {
		Backbone.Notifications.trigger('_psiturk_finishedinstructions', optmessage);
	};
	
	this.teardownTask = function(optmessage) {
		Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
	};
	return this;
};

// vi: noexpandtab nosmartindent shiftwidth=4 tabstop=4
