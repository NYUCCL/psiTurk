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
                    html = matches[0].get('html');
                } else {
                    html = "Page not found";
                };
                callback(html);
        },


});
var pages = new PageCollection();
pages.fetch({async:false});



/****************
 * MODEL        *
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

        // Get HTML file from collection and pass on to any callback
        getPage: function(pagename, callback) {
                pages.getHTML(pagename, callback);
        },

        // Use to add a line of data with any number of columns
        addTrialData: function(trialdata) {
                taskdata.addTrialData(trialdata);
        },

        // Use to add data value for one column. If a value already
        // exists for that column, it will be overwritten
        addTabularData: function(field, value) {
                taskdata.addTabularData(field, value);
        },

        finishInstructions: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedinstructions', optmessage);
        },

        teardownTask: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
        },

        saveData: function(callbacks) {
                taskdata.save(callbacks);
        },

};

