/* psiTurkCreateExp
   A object for making a "helper" app that
   lets you share an experiment
*/

var psiTurkChangePassword = function() {
	var self = this;

	self.loadModal = function () {
		// load some trials
		$.ajax({
			dataType: "json",
			url: "/changepassword",
			success: function(data) {
				self.template = data.template; // load the next few stims
				$('#changePasswordcontent').html(self.template);
			}
		})
	}

	self.begin = function() {
		self.loadModal();
		self.base = $('#changePassword');
		self.base.modal({
			keyboard: false,
  			show: false,
  			backdrop: 'static'
		});
		self.base.modal('show');
		$('#userprofile').popover('hide')
	}	

	self.submitForm = function() {

		$.ajax({
	           type: "POST",
	           dataType: "json",
	           url: "/changepassword",
	           data: $("#form-changepassword").serialize(), // serializes the form's elements.
	           success: function(data)
	           {
					self.template = data.template; // load the next few stims
					$('#changePasswordcontent').html(self.template);
	           }
	         });
	}

	self.cancel = function () {
		if (self.base) {
			self.base.modal('hide');
			self.base = null;
		}
	}

	self.loadModal();

	return self;
}


var psiTurkCreateExp = function (base, pages) {
	var self = this;
	self.current_frame = 0;
	self.baseSelector = base;
	self.pagesSelectors = pages;


	self.begin = function() {
		self.current_frame = 0;
		self.base = $(self.baseSelector);
		self.base.modal({
			keyboard: false,
  			show: false,
  			backdrop: 'static'
		});

		// load frame 1 by copying title from first page
		self.showPage(self.pagesSelectors[self.current_frame]);

		self.base.modal('show');
	}

	self.showPage = function(page) {
		$(page).css("display", "inline");
		// $(self.baseSelector+" .modal-dialog").remove();
		// $(page + " .modal-dialog").clone(deepWithDataAndEvents=true).appendTo(self.baseSelector);		
		// // reattach event
		// $("textarea").change(function() { $(this).text($(this).val()); });  // I can't believe I have to do this. HTML I hate you!
	}

	self.hidePage = function(page) {
		$(page).css("display","none");
		// $(page + " .modal-dialog").remove();
		// $(self.baseSelector + " .modal-dialog").clone().appendTo(page);				
	}

	self.submitFormAndClose = function(formId) {
		$(formId).submit();
		self.cancel();
	}

	self.cancel = function () {
		$(self.pagesSelectors[self.current_frame]).css("display","none");

		if (self.base) {
			self.base.modal('hide');
			self.current_frame = 0;
			self.base = null;
		}
	}

	self.next = function() {
		// save any data accumulated on last step
		self.hidePage(self.pagesSelectors[self.current_frame]);
		self.current_frame += 1;
		self.showPage(self.pagesSelectors[self.current_frame]);
	}

	self.prev = function() {
		self.hidePage(self.pagesSelectors[self.current_frame]);
		self.current_frame -= 1;
		if (self.current_frame<0) { self.current_frame = 0; }
		self.showPage(self.pagesSelectors[self.current_frame]);
	}

	return self;
}


/**
* Retrieves user's GitHub repositories based on username extracted from #github-username.   
*/ 
getRepos = function() {
  $("#repo_list").empty();  // Clear repos in case user changes names. 
  var github_user_name = $('#github-username').val();  // Scrape username from input box.
  $.ajax({
    type: "GET",
    url: "https://api.github.com/users/" + github_user_name +"/repos",
    dataType: "json",
    success: function(result) {
      for(i in result) {
        $("#repo_list").append("<option value=" + result[i].url + ">" + result[i].full_name + "</option>");
      } 
      $('#repo').fadeIn();  // Make dropdown box visible after applying correct username.
    },
    error: function(data) {
      $('#repo').fadeOut();
      alert('Sorry, no matching username found on github.com!  Please enter a correct name.');
    }
  });
  return false;
}

