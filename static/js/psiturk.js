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
		questiondata: {}
	},
	
	addTrialData: function(trialdata) {
		this.set({"data": this.get("data").concat(trialdata, "\n")});
		this.set({"currenttrial": this.get("currenttrial")+1});
	},
	
	addUnstructuredData: function(field, response) {
		qd = this.get("questiondata");
		qd[field] = response;
		this.set("questiondata", qd);
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
	
	return {
		/*  DATA: */
		pages: pages,
		images: images,
		taskdata: taskdata,
		
		/*  METHODS: */
		// Get HTML file from collection and pass on to a callback
		getPage: function(pagename, callback) {
			pages.getHTML(pagename, callback);
		},
		
		// Get a single image element and pass to callback
		getImage: function(imagename, callback) {
			images.getImage(imagename, callback);
		},
		
		// Add a line of data with any number of columns
		recordTrialData: function(trialdata) {
			taskdata.addTrialData(trialdata);
		},
		
		// Add data value for a named column. If a value already
		// exists for that column, it will be overwritten
		recordUnstructuredData: function(field, value) {
			taskdata.addUnstructuredData(field, value);
		},
		
		// Save data to server
		saveData: function(callbacks) {
			taskdata.save(undefined, callbacks);
		},
		
		// Notify app that participant has begun main experiment
		finishInstructions: function(optmessage) {
			Backbone.Notifications.trigger('_psiturk_finishedinstructions', optmessage);
		},
		
		teardownTask: function(optmessage) {
			Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
		}
	};
};

psiTurk = new PsiTurk();

// vi: noexpandtab nosmartindent shiftwidth=4 tabstop=4
