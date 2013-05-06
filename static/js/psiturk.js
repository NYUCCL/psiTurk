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

        addQuestionData: function(field, response) {
                qd = this.get("questiondata");
                qd[field] = response;
                this.set("questiondata", qd);
        },

});
var taskdata = new TaskData();


// Data handling functions
/*
var savedata = function(callbacks) {
	// TODO: app.py must be updated to accept a PUT with /data/assignmentid
	var exceptions = exceptions || [];
	taskdata.save(callbacks);
};
*/

/*******
 * API *
 ******/
var psiTurk = {

        addTrialData: function(trialdata) {
                taskdata.addTrialData(trialdata);
        },

        addQuestionData: function(field, response) {
                taskdata.addQuestionData(field, response);
        },

        finishInstructions: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedinstructions', optmessage);
        },

        teardownTask: function(optmessage) {
                Backbone.Notifications.trigger('_psiturk_finishedtask', optmessage);
        },

        saveData: function() {
                taskdata.save();
        },

};

