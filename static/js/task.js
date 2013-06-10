
/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */


/**********************
* Domain general code *
**********************/

// View functions
function appendtobody( tag, id, contents ) {
	var el = document.createElement( tag );
	el.id = id;
	el.innerHTML = contents;
	return el;
}


/********************
* TASK-GENERAL CODE *
********************/

// Globals defined initially.
var maxblocks = 1;
var keydownfun = function() {};
var currenttrial = 0;

// Task objects
var testobject;

// Data submit functions
var recordinstructtrial = function (instructname, rt ) {
	psiTurk.recordTrialData([uniqueId, "INSTRUCT", instructname, rt]);
};
var recordtesttrial = function (word, color, trialtype, resp, hit, rt ) {
	psiTurk.recordTrialData([uniqueId, currenttrial,  "TEST", word, color, hit, resp, hit, rt]);
};



/********************
* HTML manipulation
********************/

// TODO Replace with views.

var showpage = function(pagename) {
	psiTurk.getPage(pagename, replacebody);
};

var replacebody = function(pagehtml) {
	$('body').html(pagehtml);
};



/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function( screens ) {
	var instructpages = [
		"instruct.html"
	];
	
	var that = this,
		currentscreen = 0,
		timestamp;
	
	this.recordtrial = function() {
		rt = (new Date().getTime()) - timestamp;
		recordinstructtrial( currentscreen, rt  );
	};
	
	this.nextForm = function () {

		showpage(instructpages[currentscreen]);
		currentscreen = currentscreen + 1;

		timestamp = new Date().getTime();
		if ( currentscreen == instructpages.length ) {
			$('.continue').click(function() {
				that.recordtrial();
				that.startTest();
			});
		} else { $('.continue').click( function() {
				that.recordtrial();
				that.nextForm();
			});
		}
	};
	this.startTest = function() {
		psiTurk.finishInstructions();
        testobject = new TestPhase();
	};
	this.nextForm();
};


/********************
* CODE FOR TEST     *
********************/

var TestPhase = function() {
	var i,
	    that = this, // make 'this' accessble by privileged methods
	    lock,
	    stimimage,
	    buttonson,
	    prescard,
	    testcardsleft = new Array();
	
	this.hits = new Array();
	
	var acknowledgment = '<p>Thanks for your response!</p>';
	var textprompt = '<p id="prompt">Type<br> "R" for Red<br>"B" for blue<br>"G" for green.';
	showpage('test.html');
	
	var addprompt = function() {
		buttonson = new Date().getTime();
		$('#query').html( textprompt ).show();
	};
	
	var finishblock = function() {
		keydownfun = function() {}; // Should unbind keys.
		givequestionnaire();
	};
	
	var responsefun = function( e) {
		if (!listening) return;
			keyCode = e.keyCode;
		var response;
		switch (keyCode) {
			case 82:
				// "R"
				response="red";
				break;
			case 71:
				// "G"
				response="green";
				break;
			case 66:
				// "B"
				response="blue";
				break;
			default:
				response = "";
				break;
		}
		if ( response.length>0 ) {
			listening = false;
			responsefun = function() {};
			var hit = response == stim[1];
			var rt = new Date().getTime() - wordon;
			recordtesttrial(stim[0], stim[1], stim[2], response, hit, rt );
			remove_word();
			nextword();
		}
	};

	var nextword = function () {
		if (! stims.length) {
			finishblock();
		}
		else {
			stim = stims.pop();
			show_word( stim[0], stim[1] );
			wordon = new Date().getTime();
			//stimimage = testcardpaper.image( cardnames[getstim(prescard)], 0, 0, imgw, imgh);
			
			addprompt();
                        listening = true;
		}
	};
	
	//Set up stimulus.
	var R = Raphael("stim", 400, 100),
		font = "64px Helvetica";
	
	var show_word = function(text, color) {
		R.text( 200, 50, text ).attr({font: font, fill: color});
	};
	var remove_word = function(text, color) {
		R.clear();
	};
	$("body").focus().keydown(responsefun); 
        listening = false;

	var stims = [
		["SHIP", "red", "unrelated"],
		["MONKEY", "green", "unrelated"],
		["ZAMBONI", "blue", "unrelated"],
		["RED", "red", "congruent"],
		["GREEN", "green", "congruent"],
		["BLUE", "blue", "congruent"],
		["GREEN", "red", "incongruent"],
		["BLUE", "green", "incongruent"],
		["RED", "blue", "incongruent"]
		];
	_.shuffle(stims);
	nextword();
	return this;
};

/****************
* Questionnaire *
****************/

var taskfinished = function() { window.location="/debrief?uniqueId=" + psiTurk.taskdata.id; };

// We may want this to end up being a backbone view
var givequestionnaire = function() {
	
	var timestamp = new Date().getTime();
	showpage('postquestionnaire.html');
	recordinstructtrial("postquestionnaire", (new Date().getTime())-timestamp );
	
	$("#continue").click(function () {
		recordQuestionnaire();
		psiTurk.teardownTask();
    	psiTurk.saveData({success: function() {taskfinished();}, error: prompt_to_resubmit});
		taskfinished();
	});
};

var promptResubmit = function() {
	replacebody("<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>");
	$("#resubmit").click(finishTask);
};

var finishTask = function() {
	replacebody("<h1>Trying to resubmit...</h1>");
	reprompt = setTimeout(prompt_to_resubmit, 10000);
	psiTurk.saveData({success: function() {clearInterval(reprompt); taskfinished();}, error: promptResubmit});
};



var recordQuestionnaire = function() {
	$('textarea').each( function(i, val) {
        psiTurk.recordUnstructuredData(this.id, this.value);
	});
	$('select').each( function(i, val) {
        psiTurk.recordUnstructuredData(this.id, this.value);		
	});
};

var prompt_to_resubmit = function() {
};


/*******************
 * Run Task
 ******************/
$(window).load( function(){
	instructobject = new Instructions(['instruct']);
});

// vi: noexpandtab tabstop=4 shiftwidth=4
