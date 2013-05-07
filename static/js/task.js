
/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */

// Global variables
var optoutmessage = "By leaving this page, you opt out of the experiment.  You are forfitting your $1.00 payment and your 1/10 chance to with $10. Please confirm that this is what you meant to do.";

/**********************
* Domain general code *
**********************/

// Helper functions

// We want to be able to alias the order of stimuli to a single number which
// can be stored and which can easily replicate a given stimulus order.
function changeorder(arr, ordernum) {
	var thisorder = ordernum;
	var shufflelocations = new Array();
	for (var i=0; i<arr.length; i++) {
		shufflelocations.push(i);
	}
	for (i=arr.length-1; i>=0; --i) {
		var loci = shufflelocations[i];
		var locj = shufflelocations[thisorder%(i+1)];
		thisorder = Math.floor(thisorder/(i+1));
		var tempi = arr[loci];
		var tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	return arr;
}

// Fisher-Yates shuffle algorithm, with "exceptions," indices that don't change order
function shuffle(arr, exceptions) {
	var i;
	exceptions = exceptions || [];
	var shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
		// Create a list of candidate shuffle locations, excluding exceptions.
		if (exceptions.indexOf(i)==-1) { shufflelocations.push(i); }
	}
	for (i=shufflelocations.length-1; i>=0; --i) {
		var loci = shufflelocations[i];
		var locj = shufflelocations[randrange(0, i+1)];
		var tempi = arr[loci];
		var tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	return arr;
}

// This function swaps two array members at random, provided they are not in
// the exceptions list.
function swap(arr, exceptions) {
	var i;
	var except = exceptions ? exceptions : [];
	var shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
		if (except.indexOf(i)==-1) shufflelocations.push(i);
	}

	for (i=shufflelocations.length-1; i>=0; --i) {
		var loci = shufflelocations[i];
		var locj = shufflelocations[randrange(0,i+1)];
		var tempi = arr[loci];
		var tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	return arr;
}

// Mean of booleans (true==1; false==0)
function boolpercent(arr) {
	var count = 0;
	for (var i=0; i<arr.length; i++) {
		if (arr[i]) { count++; } 
	}
	return 100* count / arr.length;
}

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

// Stimulus info
var ncards = 2,
    cardnames = [
	"static/images/STIM00.PNG",
	"static/images/STIM01.PNG",
	"static/images/STIM02.PNG",
	"static/images/STIM03.PNG",
	"static/images/STIM04.PNG",
	"static/images/STIM05.PNG",
	"static/images/STIM06.PNG",
	"static/images/STIM07.PNG",
	"static/images/STIM08.PNG",
	"static/images/STIM09.PNG",
	"static/images/STIM10.PNG",
	"static/images/STIM11.PNG",
	"static/images/STIM12.PNG",
	"static/images/STIM13.PNG",
	"static/images/STIM14.PNG",
	"static/images/STIM15.PNG"],
	categorynames= [ "A", "B" ];

// Interface variables
var cardh = 180, cardw = 140, upper = 0, left = 0, imgh = 100, imgw = 100;

// Task objects
var testobject;

// Data submit functions
var recordinstructtrial = function (instructname, rt ) {
	psiTurk.addTrialData([workerId, assignmentId, "INSTRUCT", instructname, rt]);
};
var recordtesttrial = function (word, color, trialtype, resp, hit, rt ) {
	psiTurk.addTrialData([workerId, assignmentId, currenttrial,  "TEST", word, color, hit, resp, hit, rt]);
};




/********************
* HTML snippets
********************/

var showpage = function(pagename) {
	psiTurk.getPage(pagename, replacebody);
};

var replacebody = function(pagehtml) {
	$('body').html(pagehtml);
};

var instructpages = [
	"instruct.html"
];



/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function( screens ) {
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
		};
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
	shuffle( stims );
	nextword();
	return this;
};

/****************
* Questionnaire *
****************/

// TODO this url needs to bring the next screen, we're no longer doing it with a POST
// Also questionnaire answers are now saved separately from the main csv.
var thanksurl = "/thanks";
// TODO: Make posterror prompt to resubmit.
var posterror = function() { alert( "There was an error submitting." ); };
// TODO: Make sure taskfinished works properly
//var taskfinished = function() { window.location = thanksurl; };
var taskfinished = function() { showpage('thanks.html') };

// We may want this to end up being a backbone view
var givequestionnaire = function() {
	var timestamp = new Date().getTime();
	showpage('postquestionnaire.html');
	recordinstructtrial("postquestionnaire", (new Date().getTime())-timestamp );
	$("#continue").click(function () {
		addqustionnaire();
		psiTurk.teardownTask();
    	psiTurk.saveData({error: posterror, success: taskfinished});

	});
	// $('#continue').click( function(){ trainobject = new TrainingPhase(); } );
	// postback();
};
var addqustionnaire = function() {
	$('textarea').each( function(i, val) {
        psiTurk.addTabularData(this.id, this.value);
	});
	$('select').each( function(i, val) {
        psiTurk.addTabularData(this.id, this.value);		
	});
};


// vi: et! ts=4 sw=4
