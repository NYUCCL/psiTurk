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
	// Provide opt-out 
	$(window).on("beforeunload", function(){
		$.ajax("quitter", {
				type: "POST",
				async: false,
				data: {assignmentId: assignmentId, workerId: workerId, dataString: datastring}
		});
		alert(msg);
		return "Are you sure you want to leave the experiment?";
	});
};

var TaskView = Backbone.View.extend({
	initialize: function() {
		Backbone.Notifications.on('_psiturk_finishedistructions', startTask);
		Backbone.Notifications.on('_psiturk_finishedtask', function(msg) {
			$(window).off("beforeunload");
		});
	}
});

/****************
 * MODEL        *
 ***************/

var taskdata = Backbone.Model.extend({
	url: "/data", // Save will PUT to /data, with mimetype 'application/JSON'
	id: assignmentid,  // Determines the sync url, TODO make sure htis is unique!
	addtrial: function(trialinfo) {
		this.trials = this.trials.concat(trialinfo, "\n" );
		this.currenttrial++;
	},
	currenttrial: 0,
	trials: ""
});

// Data handling functions

var savedata = function(callbacks) {
	// TODO: app.py must be updated to accept a PUT with /data/assignmentid
	var exceptions = exceptions || [];
	taskdata.save(callbacks);
};


/*******
 * API *
 ******/

var finishInstructions = function(optmessage) {
	Backbone.Notifications.trigger('_psiturk_finishedistructions', optmessage);
};

var teardownTask = function(optmessage) {
	Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
};
