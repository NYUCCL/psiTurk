
/**********************
* Domain general code *
**********************/

// Helper functions

// Assert functions stolen from 
// http://aymanh.com/9-javascript-tips-you-may-not-know#assertion
function AssertException(message) { this.message = message; }
AssertException.prototype.toString = function () {
	return 'AssertException: ' + this.message;
};

function assert(exp, message) {
	if (!exp) {
		throw new AssertException(message);
	}
}

function insert_hidden_into_form(findex, name, value ) {
	var form = document.forms[findex];
	var hiddenField = document.createElement('input');
	hiddenField.setAttribute('type', 'hidden');
	hiddenField.setAttribute('name', name);
	hiddenField.setAttribute('value', value );
	form.appendChild( hiddenField );
}


// Preload images (not currently in use)
function imagepreload(src) 
{
	var heavyImage = new Image(); 
	heavyImage.src = src;
}

/** 
 * SUBSTITUTE PLACEHOLDERS WITH string values 
 * @param {String} str The string containing the placeholders 
 * @param {Array} arr The array of values to substitute 
 * From Fotiman on this forum:
 * http://www.webmasterworld.com/javascript/3484761.htm
 */ 
function substitute(str, arr) 
{ 
	var i, pattern, re, n = arr.length; 
	for (i = 0; i < n; i++) { 
		pattern = "\\{" + i + "\\}"; 
		re = new RegExp(pattern, "g"); 
		str = str.replace(re, arr[i]); 
	} 
	return str; 
} 

function randrange ( lower, upperbound ) {
	// Finds a random integer from 'lower' to 'upperbound-1'
	return Math.floor( Math.random() * upperbound + lower );
}

// We want to be able to alias the order of stimuli to a single number which
// can be stored and which can easily replicate a given stimulus order.
function changeorder( arr, ordernum ) {
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

// Fisher-Yates shuffle algorithm.
// modified from http://sedition.com/perl/javascript-fy.html
function shuffle( arr, exceptions ) {
	var i;
	exceptions = exceptions || [];
	var shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
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
function swap( arr, exceptions ) {
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

// Data submission
// NOTE: Ended up not using this.
function posterror() { alert( "There was an error. TODO: Prompt to resubmit here." ); }
function submitdata() {
	$.ajax("submit", {
			type: "POST",
			async: false,
			data: {datastring: datastring},
			// dataType: 'text',
			success: thanks,
			error: posterror
	});
}

/********************
* TASK-GENERAL CODE *
********************/

// Globals defined initially.
var maxblocks = 2;
var keydownfun = function() {};

// Stimulus info
var ncards = 8,
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

// Mutable global variables
var responsedata = [],
    currenttrial = 1,
    datastring = "",
    lastperfect = false;

// Data handling functions
function recordinstructtrial (instructname, rt ) {
	trialvals = [assignmentId, "INSTRUCT", instructname, rt];
	datastring = datastring.concat( trialvals, "\n" );
}
function recordtesttrial (word, color, trialtype, resp, hit, rt ) {
	trialvals = [assignmentId, currenttrial,  "TEST", word, color, hit, resp, hit, rt];
	datastring = datastring.concat( trialvals, "\n" );
	currenttrial++;
}

/********************
* HTML snippets
********************/
var pages = {};

var showpage = function(pagename) {
	$('body').html( pages[pagename] );
};

var pagenames = [
	"postquestionnaire",
	"test",
	"instruct"
];


/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function( screens ) {
	var that = this,
		currentscreen = "",
		timestamp;
	for( i=0; i<screens.length; i++) {
		pagename = screens[i];
		$.ajax({ 
			url: pagename + ".html",
			success: function(pagename){ return function(page){ pages[pagename] = page; }; }(pagename),
			async: false
		});
	}

	this.recordtrial = function() {
		rt = (new Date().getTime()) - timestamp;
		recordinstructtrial( currentscreen, rt  );
	};
	
	this.nextForm = function () {
		var next = screens.splice(0, 1)[0];
		currentscreen = next;
		showpage( next );
		timestamp = new Date().getTime();
		if ( screens.length === 0 ) $('.continue').click(function() {
			that.recordtrial();
			that.startTest();
		});
		else $('.continue').click( function() {
			that.recordtrial();
			that.nextForm();
		});
	};
	this.startTest = function() {
		// startTask();
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
	showpage( 'test' );
	
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
			recordtesttrial (stim[0], stim[1], stim[2], response, hit, rt );
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

/*************
* Finish up  *
*************/
var givequestionnaire = function() {
	var timestamp = new Date().getTime();
	showpage('postquestionnaire');
	recordinstructtrial( "postquestionnaire", (new Date().getTime())-timestamp );
	$("#continue").click(function () {
		finish();
		submitquestionnaire();
	});
	// $('#continue').click( function(){ trainobject = new TrainingPhase(); } );
	// postback();
};
var submitquestionnaire = function() {
	$('textarea').each( function(i, val) {
		datastring = datastring.concat( "\n", this.id, ":",  this.value);
	});
	$('select').each( function(i, val) {
		datastring = datastring.concat( "\n", this.id, ":",  this.value);
	});
	insert_hidden_into_form(0, "assignmentid", assignmentId );
	insert_hidden_into_form(0, "data", datastring );
	$('form').submit();
};

var startTask = function () {
	// Provide opt-out 
	window.onbeforeunload = function(){
		$.ajax("quitter", {
				type: "POST",
				async: false,
				data: {assignmentId: assignmentId, dataString: datastring}
		});
		alert( "By leaving this page, you opt out of the experiment.  You are forfitting your $1.00 payment and your 1/10 chance to with $10. Please confirm that this is what you meant to do." );
		return "Are you sure you want to leave the experiment?";
	};
};

var finish = function () {
	window.onbeforeunload = function(){ };
};

// vi: et! ts=4 sw=4
