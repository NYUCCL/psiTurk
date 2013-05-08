/*
 * Requires:
 *     jquery
 *     backbone
 */


/****************
 * Internals    *
 ***************/

// Sets up global notifications pub/sub
Backbone.Notifications = {};
_.extend(Backbone.Notifications, Backbone.Events);

var startTask = function (msg) {

        taskdata.save();

	$.ajax("inexp", {
			type: "POST",
			async: true,
			data: {assignmentId: assignmentId}
	});
        
	// Provide opt-out 
	$(window).on("beforeunload", function(){

                taskdata.save();

		$.ajax("quitter", {
				type: "POST",
				async: false,
				data: {assignmentId: assignmentId, workerId: workerId, dataString: ""}
		});
		alert(msg);
		return "Are you sure you want to leave the experiment?";
	});
};

var TaskView = Backbone.View.extend({

	initialize: function() {

		Backbone.Notifications.on('_psiturk_finishedinstructions', startTask);

		Backbone.Notifications.on('_psiturk_finishedtask', function(msg) {
			$(window).off("beforeunload");
		});
	},

});
var taskview = new TaskView();


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
                if (matches.length > 0) {
                    callback(matches[0].get('html'));
                } else {
                    console.log("Page not found: ", pagename);
                };
        },


});
var pages = new PageCollection();
pages.fetch({async: false});


/****************
 * IMAGES       *
 ***************/
var ExpImage = Backbone.Model.extend({
        defaults: {
                name: "",
                loc: "",
                el: null,
        },

        initialize: function() {
                var img = new Image();
                img.src = this.get('loc');
                this.set('el', img);
        },
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
                };
        },
});
var images = new ImageCollection();


/****************
 * TASK DATA    *
 ***************/
var TaskData = Backbone.Model.extend({

        urlRoot: "/data", // Save will PUT to /data, with mimetype 'application/JSON'
        id: assignmentId,

        defaults: {
                currenttrial: 0,
                data: "",
                questiondata: {}
        },

        addTrialData: function(trialdata) {
                this.set({"data": this.get("data").concat(trialdata, "\n")});
                this.set({"currenttrial": this.get("currenttrial")+1});
        },

        addTabularData: function(field, response) {
                qd = this.get("questiondata");
                qd[field] = response;
                this.set("questiondata", qd);
        },

});
var taskdata = new TaskData();


/*******
 * API *
 ******/
var psiTurk = {

        // Get HTML file from collection and pass on to a callback
        getPage: function(pagename, callback) {
                pages.getHTML(pagename, callback);
        },

        // Preload images from static/images (not done by default)
        preloadImages: function() {
                images.fetch({async: false});
        },
        
        // Get a single image element and pass to callback
        getImage: function(imagename, callback) {
                images.getImage(imagename, callback);
        },

        // Add a line of data with any number of columns
        addTrialData: function(trialdata) {
                taskdata.addTrialData(trialdata);
        },

        // Add data value for a named column. If a value already
        // exists for that column, it will be overwritten
        addTabularData: function(field, value) {
                taskdata.addTabularData(field, value);
        },

        // Sync data with server
        saveData: function(callbacks) {
                taskdata.save(callbacks);
        },
        
        // Notify app that participant has begun main experiment
        finishInstructions: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedinstructions', optmessage);
        },

        teardownTask: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
        },

};

