
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

function randrange(lower, upperbound) {
	// Finds a random integer from 'lower' to 'upperbound-1'
	return Math.floor( Math.random() * upperbound + lower );
}
