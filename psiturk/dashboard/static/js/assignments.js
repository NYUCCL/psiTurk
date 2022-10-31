import { DatabaseView } from "./dbview.js";
import { DatabaseFilters } from "./dbfilter.js";

// The fields to be parsed from the returned HIT response
var ASSIGNMENT_FIELDS = {
  workerId: { title: "Worker ID", type: "string", style: { width: "200px" } },
  assignmentId: {
    title: "Assignment ID",
    type: "string",
    style: { "max-width": "150px" },
  },
  status: { title: "Status", type: "string", style: { width: "100px" } },
  bonused: { title: "Bonused", type: "dollar", style: { width: "100px" } },
  accept_time: {
    title: "Accepted On",
    type: "date",
    style: { width: "300px" },
  },
  submit_time: {
    title: "Submitted On",
    type: "date",
    style: { width: "300px" },
  },
};

// The fields to use in the approval HIT display
var APPROVE_FIELDS = {
  workerId: { title: "Worker ID", type: "string", style: { width: "200px" } },
  status: { title: "Status", type: "string", style: { width: "100px" } },
  assignmentId: {
    title: "Assignment ID",
    type: "string",
    style: { width: "320px" },
  },
};

// The fields to use in the bonus HIT display
var BONUS_FIELDS = {
  workerId: { title: "Worker ID", type: "string", style: { width: "200px" } },
  bonus: { title: "Bonus", type: "dollar", style: { width: "100px" } },
  bonused: { title: "Bonused", type: "dollar", style: { width: "100px" } },
  status: { title: "Status", type: "string", style: { width: "100px" } },
  assignmentId: {
    title: "Assignment ID",
    type: "string",
    style: { width: "320px" },
  },
};

// For a local hit, add code version and bonus, as well as data fields
if (HIT_LOCAL) {
  ASSIGNMENT_FIELDS = {
    workerId: { title: "Worker ID", type: "string", style: { width: "200px" } },
    assignmentId: {
      title: "Assignment ID",
      type: "string",
      style: { "max-width": "150px" },
    },
    status: { title: "Status", type: "string", style: { width: "100px" } },
    bonus: { title: "Bonus", type: "dollar", style: { width: "100px" } },
    bonused: { title: "Bonused", type: "dollar", style: { width: "100px" } },
    codeversion: { title: "Code#", type: "string", style: { width: "100px" } },
    accept_time: {
      title: "Accepted On",
      type: "date",
      style: { width: "300px" },
    },
    submit_time: {
      title: "Submitted On",
      type: "date",
      style: { width: "300px" },
    },
  };

  var DATA_FIELDS = {
    event_data: {
      eventtype: {
        title: "Event Type",
        type: "string",
        style: { width: "200px" },
      },
      value: { title: "Value", type: "json", style: { width: "200px" } },
      interval: { title: "Interval", type: "num", style: { width: "100px" } },
    },
    question_data: {
      questionname: {
        title: "Question Name",
        type: "string",
        style: { width: "200px" },
      },
      response: {
        title: "Response",
        type: "json",
        style: { width: "200px", "max-width": "600px" },
      },
    },
    trial_data: {
      current_trial: { title: "Trial", type: "num", style: { width: "100px" } },
      trialdata: {
        title: "Data",
        type: "json",
        style: { width: "200px", "max-width": "600px" },
      },
      dateTime: { title: "Time", type: "date", style: { width: "200px" } },
    },
  };
}

class AssignmentsDBDisplay {
  // Create the assignments display with references to the HTML elements it will
  // use as a basis for controls and in which it will fill in the database.
  constructor(domelements) {
    this.DOM$ = domelements;
    this.db = undefined; // Main assignment database handler
    this.assignmentSelected = false; // Is an assignment selected currently?
  }

  // Build the database views into their respective elmeents. There is one
  // for the main database and another for the sub-assignments view
  init() {
    this.dbfilters = new DatabaseFilters(this.DOM$, ASSIGNMENT_FIELDS, {
      onChange: this._filterChangeHandler.bind(this),
      onDownload: this._downloadTableHandler.bind(this),
    });
    this.db = new DatabaseView(
      this.DOM$,
      {
        onSelect: this._assignmentSelectedHandler.bind(this),
      },
      "assignments",
      this.dbfilters
    );

    // Load the data
    this._loadAssignments(HIT_ID);
  }

  // Pulls the assignment data from the backend and loads it into the main database
  _loadAssignments(hitId) {
    $.ajax({
      type: "POST",
      url: "/api/assignments/",
      data: JSON.stringify({
        hit_ids: [hitId],
        local: HIT_LOCAL,
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: (data) => {
        if (data.length > 0) {
          this.db.updateData(data, ASSIGNMENT_FIELDS, {
            rerender: true,
            resetFilter: false,
            maintainSelected: false,
            index: "assignmentId",
            callback: () => {
              this._loadBonusesPaid(HIT_ID);
            },
          });
        }
      },
      error: function (errorMsg) {
        alert(errorMsg);
        console.log(errorMsg);
      },
    });
  }

  // Gets bonus information about the HIT
  _loadBonusesPaid(hitId) {
    $.ajax({
      type: "POST",
      url: "/api/bonuses",
      data: JSON.stringify({
        hit_id: hitId,
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: (bonusData) => {
        let bonuses = {};
        bonusData.bonuses.forEach((bonus) => {
          if (bonuses[bonus["assignmentId"]] == undefined) {
            bonuses[bonus["assignmentId"]] = bonus["bonusAmount"];
          } else {
            bonuses[bonus["assignmentId"]] += bonus["bonusAmount"];
          }
        });
        let updatedData = this.db.data;
        updatedData.forEach((el, i) => {
          updatedData[i]["bonused"] = bonuses[el["assignmentId"]];
        });
        this.db.updateData(updatedData, ASSIGNMENT_FIELDS, {
          rerender: true,
          resetFilter: false,
          maintainSelected: true,
          index: "assignmentId",
          callback: () => {
            if (ASSIGNMENT_ID) {
              $("#" + this.db.trPrefix + ASSIGNMENT_ID).click();
            }
          },
        });
      },
      error: function (errorMsg) {
        alert(errorMsg);
        console.log(errorMsg);
      },
    });
  }

  // Reloads specific assignment data
  _reloadAssignments(assignment_ids) {
    $.ajax({
      type: "POST",
      url: "/api/assignments/",
      data: JSON.stringify({
        assignment_ids: assignment_ids,
        local: HIT_LOCAL,
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: (data) => {
        let updatedData = this.db.data;
        data.forEach((el, _) => {
          let i = updatedData.findIndex(
            (o) => o["assignmentId"] == el["assignmentId"]
          );
          updatedData[i] = el;
        });
        this.db.updateData(updatedData, ASSIGNMENT_FIELDS, {
          rerender: true,
          resetFilter: false,
          maintainSelected: true,
          index: "assignmentId",
          callback: () => {
            this._loadBonusesPaid(HIT_ID);
          },
        });
      },
      error: function (errorMsg) {
        console.log(errorMsg);
      },
    });
  }

  /**
   * HANDLER: Change in filters of main DB view
   */
  _filterChangeHandler() {
    this.db.renderTable();
  }

  /**
   * HANDLER: Download table
   */
  _downloadTableHandler() {
    this.db.downloadData("assignments_" + HIT_ID);
  }

  // Handler for assignment select
  _assignmentSelectedHandler(data) {
    $("#assignmentInfo_hitid").text(data["hitId"]);
    $("#assignmentInfo_workerid").text(data["workerId"]);
    $("#assignmentInfo_assignmentid").text(data["assignmentId"]);
    $("#assignmentInfo_status").text(data["status"]);
    $("#assignmentInfo_accepted").text(data["accept_time"]);
    $("#assignmentInfo_submitted").text(data["submit_time"]);

    // Update approval / rejection buttons
    $("#approveOne").prop(
      "disabled",
      !["Submitted", "Rejected"].includes(data["status"])
    );
    $("#rejectOne").prop("disabled", data["status"] != "Submitted");
    $("#bonusOne").prop(
      "disabled",
      !["Credited", "Approved"].includes(data["status"])
    );

    if (HIT_LOCAL) {
      $("#assignmentInfo_bonus").text("$" + data["bonus"].toFixed(2));
      $("#downloadOneData").prop("disabled", data["status"] == "Allocated");
      $("#viewOneData").prop("disabled", data["status"] == "Allocated");
      // Update the data download HREF
      if (data["status"] != "Allocated") {
        $("#downloadOneDataHref").attr(
          "href",
          "/api/assignments/action/datadownload?assignmentid=" +
            data["assignmentId"]
        );
      } else {
        $("#downloadOneDataHref").removeAttr("href");
      }
    } else {
      $("#assignmentInfo_bonus").text("???");
    }
    $("#assignmentInfo_bonused").text(
      data["bonused"] ? "$" + data["bonused"] : undefined
    );

    // Update the current HREF
    history.pushState(
      { id: "hitpage" },
      "",
      window.location.origin +
        "/dashboard/hits/" +
        HIT_ID +
        "/assignments/" +
        data["assignmentId"]
    );
  }
}

class AssignmentWorkerDataDBDisplay {
  // Create the assignments worker data display
  constructor(domelements) {
    this.DOM$ = domelements;
    this.db = undefined; // Main assignment database handler
    this.dataCache = {}; // { id: { questions, events, trials } }
  }

  // Build the database view, do not load with data yet.
  init() {
    this.db = new DatabaseView(
      this.DOM$,
      {
        onSelect: function () {},
      },
      "workerdata"
    );
  }

  // Loads a worker's data from the database into the cache
  _loadWorkerData(assignment_id, callback) {
    if (!(assignment_id in this.dataCache)) {
      $.ajax({
        type: "POST",
        url: "/api/assignments/action/data",
        data: JSON.stringify({
          assignments: [assignment_id],
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: (data) => {
          this.dataCache[assignment_id] = data[assignment_id];
          callback();
        },
        error: function (errorMsg) {
          console.log(errorMsg);
        },
      });
    } else {
      callback();
    }
  }

  // Loads the worker data from the cache into the database
  async displayWorkerData(assignment_id) {
    this._loadWorkerData(assignment_id, () => {
      let type = $('input[name="dataRadioOptions"]:checked').val();
      this.db.updateData(
        this.dataCache[assignment_id][type],
        DATA_FIELDS[type],
        {
          rerender: true,
          resetFilter: false,
          maintainSelected: false,
          index: undefined,
          callback: () => {},
        }
      );
    });
  }
}

// Approves a list of assignment ids and then reloads them
function assignmentAPI(assignment_ids, endpoint, payload = {}, reload = true) {
  return new Promise((resolve, reject) => {
    $.ajax({
      type: "POST",
      url: "/api/assignments/action/" + endpoint,
      data: JSON.stringify({
        assignments: assignment_ids,
        all_studies: !HIT_LOCAL,
        ...payload,
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function (data) {
        if (data.every((el) => !el.success)) {
          reject();
        } else {
          if (reload) {
            mainDisp._reloadAssignments(assignment_ids);
          }
          resolve();
        }
      },
      error: function (errorMsg) {
        console.log(errorMsg);
        reject();
      },
    });
  });
}

// Worker API, used mainly for notifyinig workers
function workersAPI(worker_ids, endpoint, payload = {}, reload = false) {
  return new Promise((resolve, reject) => {
    $.ajax({
      type: "POST",
      url: "/api/workers/action/" + endpoint,
      data: JSON.stringify({
        worker_ids: worker_ids,
        ...payload,
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function (data) {
        if (data.every((el) => !el.success)) {
          reject();
        } else {
          if (reload) {
            mainDisp._reloadAssignments(assignment_ids);
          }
          resolve();
        }
      },
      error: function (errorMsg) {
        console.log(errorMsg);
        reject();
      },
    });
  });
}

// Approves a single individual in the database
function approveIndividualHandler() {
  let assignment_id = $("#assignmentInfo_assignmentid").text();
  $("#approveOne").prop("disabled", true);
  $("#rejectOne").prop("disabled", true);
  assignmentAPI([assignment_id], "approve", {})
    .then(() => {
      alert("Approval successful!");
    })
    .catch(() => {
      $("#approveOne").prop("disabled", false);
      $("#rejectOne").prop("disabled", false);
      alert("Approval unsuccessful");
    });
}

// Approves all the individuals in the approval display
function approveAllHandler() {
  let assignment_ids = approvalDispView
    .getDisplayedData()
    .map((el) => el["assignmentId"]);
  $("#approval-submit").prop("disabled", true);
  assignmentAPI(assignment_ids, "approve", {})
    .then(() => {
      $("#approveModal").modal("hide");
      $("#approval-submit").prop("disabled", false);
      alert("Approval successful!");
    })
    .catch(() => {
      $("#approval-submit").prop("disabled", false);
      alert("Approval unsuccessful.");
    });
}

// Rejects a single individual in the database
function rejectIndividualHandler() {
  let assignment_id = $("#assignmentInfo_assignmentid").text();
  $("#approveOne").prop("disabled", true);
  $("#rejectOne").prop("disabled", true);
  assignmentAPI([assignment_id], "reject", {})
    .then(() => {
      alert("Rejection successful!");
    })
    .catch(() => {
      $("#approveOne").prop("disabled", false);
      $("#rejectOne").prop("disabled", false);
      alert("Rejection unsuccessful");
    });
}

var bonusesUploaded;
function bonusAllHandler() {
  let displayedData = bonusDispView.getDisplayedData();
  let assignment_ids = displayedData.map((el) => el["assignmentId"]);
  let amount = parseFloat($("#bonus-value").val());
  if ($("#bonus-autoToggle").hasClass("active")) {
    amount = "auto";
  }
  let reason = $("#bonus-reason").val();
  if (!reason) {
    if (BONUS_REASON) {
      reason = BONUS_REASON;
    } else {
      alert("No bonus reason given, and default bonus_message not set!");
      return;
    }
  }
  $("#bonus-submit").prop("disabled", true);
  // in case of custom bonus amounts
  if (amount == "auto" && bonusesUploaded != undefined) {
    // bonus each worker, and wait for all to complete
    assignment_ids = [];
    let bonusPromises = displayedData.reduce((result, el) => {
      if (bonusesUploaded[el["workerId"]]) {
        assignment_ids.push(el["assignmentId"]);
        result.push(
          assignmentAPI(
            el["assignmentId"],
            "bonus",
            {
              amount: bonusesUploaded[el["workerId"]],
              reason: reason,
            },
            false
          )
        );
      }
      return result;
    }, []);
    // once all complete, notify how many succeeded and how many failed
    Promise.allSettled(bonusPromises).then((results) => {
      let statuses = results.reduce(
        (acc, result) => {
          acc[result.status == "fulfilled" ? 0 : 1] += 1;
          return acc;
        },
        [0, 0]
      );
      let status = [];
      if (statuses[0] > 0)
        status.push(`Successfully bonused ${statuses[0]} workers!`);
      if (statuses[1] > 0)
        status.push(`Failed to bonus ${statuses[1]} workers.`);
      // update the assignments
      mainDisp._reloadAssignments(assignment_ids);
      // alert of status and close the modal
      alert(status.join(" "));
      $("#bonusModal").modal("hide");
      $("#bonus-submit").prop("disabled", false);
    });
    // otherwise let the API handle everything
  } else {
    assignmentAPI(assignment_ids, "bonus", { amount, reason })
      .then(() => {
        $("#bonusModal").modal("hide");
        $("#bonus-submit").prop("disabled", false);
        alert("Bonus successful!");
      })
      .catch(() => {
        $("#bonus-submit").prop("disabled", false);
        alert("Bonus unsuccessful");
      });
  }
}

// Opens the worker approval modal with the workers currently in the table
var approvalDispView;
function approveWorkersModal() {
  let assignments = mainDisp.db.getDisplayedData();
  assignments = assignments.filter((data) => data["status"] == "Submitted");
  if (!approvalDispView) {
    approvalDispView = new DatabaseView({ display: $("#DBApprovalTable") });
  }
  approvalDispView.updateData(assignments, APPROVE_FIELDS);
  $("#numWorkersApproving").text(assignments.length);
  $("#approval-numWorkers").text(assignments.length);

  // MTurk fee is 20% for HITs with < 10 assignments, 40% for HITs with 10 or more
  let mturkfee = HIT_ASSIGNMENTS > 9 ? 0.4 : 0.2;
  let totalCost = HIT_REWARD * (1 + mturkfee) * assignments.length;
  $("#approval-mturkfee").text(100 * mturkfee);
  $("#approval-total").text(totalCost.toFixed(2));

  // If no workers, do not enable the approve
  if (assignments.length == 0) {
    $("#approval-submit").prop("disabled", true);
  } else {
    $("#approval-submit").prop("disabled", false);
  }
}

// Handler for bonus information changing
function bonusInfoChanged() {
  let assignments = mainDisp.db.getDisplayedData();
  $("#bonus-autoToggle").prop("disabled", !HIT_LOCAL && !bonusesUploaded);

  // Find base total
  let total = assignments.length * $("#bonus-value").val();
  let totalText = `${$("#bonus-value").val()} x ${assignments.length}`;
  if ($("#bonus-autoToggle").hasClass("active")) {
    total = bonusDispView
      .getDisplayedData()
      .reduce(
        (prevValue, el) => prevValue + (el["bonus"] ? el["bonus"] : 0),
        0
      );
    totalText = total.toFixed(2);
  }
  $("#bonus-baseTotal").text(totalText);

  // MTurk fee is 20% for HITs with < 10 assignments, 40% for HITs with 10 or more
  let mturkfee = HIT_ASSIGNMENTS > 9 ? 0.4 : 0.2;
  $("#bonus-mturkfee").text(100 * mturkfee);

  // Now set grand total
  $("#bonus-total").text((total * (1 + mturkfee)).toFixed(2));
}

// Opens the worker bonus modal with the workers currently in the table
var bonusDispView;
function bonusWorkersModal() {
  let assignments = mainDisp.db.getDisplayedData();
  assignments = assignments.filter((data) =>
    ["Credited", "Approved"].includes(data["status"])
  );
  if (!bonusDispView) {
    bonusDispView = new DatabaseView({ display: $("#DBBonusTable") });
  }
  bonusesUploaded = undefined;
  bonusDispView.updateData(assignments, BONUS_FIELDS);
  $("#numWorkersBonusing").text(assignments.length);
  bonusInfoChanged();
}

// Reads a CSV of worker bonuses into bonusesUploaded
function handleBonusFileUpload(event) {
  const reader = new FileReader();
  reader.onload = (event) => {
    bonusesUploaded = {};
    const lines = event.target.result.split("\n");
    for (let i = 1; i < lines.length; i++) {
      let cols = lines[i].split(",");
      bonusesUploaded[cols[0]] = parseFloat(cols[1]);
    }
    let newAssignments = [...bonusDispView.getDisplayedData()];
    for (let i = 0; i < newAssignments.length; i++) {
      if (bonusesUploaded[newAssignments[i]["workerId"]] != undefined) {
        newAssignments[i] = {
          ...newAssignments[i],
          bonus: bonusesUploaded[newAssignments[i]["workerId"]],
        };
      }
    }
    bonusDispView.updateData(newAssignments, BONUS_FIELDS);
    $("#bonus-file").val("");
    $("#bonus-autoToggle").click();
    bonusInfoChanged();
  };
  reader.readAsText(event.target.files[0]);
}

// Opens the worker bonus modal with the single worker selected
function bonusOneWorkerModal() {
  let assignment_id = $("#assignmentInfo_assignmentid").text();
  let assignments = mainDisp.db.getDisplayedData();
  assignments = assignments.filter(
    (data) => data["assignmentId"] == assignment_id
  );
  if (!bonusDispView) {
    bonusDispView = new DatabaseView({ display: $("#DBBonusTable") });
  }
  bonusDispView.updateData(assignments, BONUS_FIELDS);
  $("#numWorkersBonusing").text(assignments.length);
  bonusInfoChanged();
  $("#bonusModal").modal("show");
}

// Listens for modal showing and loads in worker data for an assignment
function viewWorkerDataHandler() {
  let assignment_id = $("#assignmentInfo_assignmentid").text();
  dataDisp.displayWorkerData(assignment_id);
  $("#workerDataAssignmentId").text(assignment_id);
}

// Populates the table view with assignments, loads handlers
var mainDisp;
var dataDisp;
$(window).on("load", function () {
  // Initialize the assignment display
  mainDisp = new AssignmentsDBDisplay({
    filters: $("#DBFilters"),
    display: $("#DBDisplay"),
  });
  mainDisp.init();

  // Initialize worker data display
  dataDisp = new AssignmentWorkerDataDBDisplay({
    display: $("#DataDBDisplay"),
  });
  dataDisp.init();

  // Listeners for moving with arrow keys
  $(document).keydown((e) => {
    if (e.which == 38) {
      mainDisp.db.selectPreviousRow();
    } else if (e.which == 40) {
      mainDisp.db.selectNextRow();
    }
  });

  // On view worker data request, load in the data
  $("#downloadOneData").on("click", () => {
    // mainDisp._reloadAssignments(['3I3WADAZ9Q5QECKJM5NCXE9VS1X5OL']);
  });
  $("#viewOneData").on("click", viewWorkerDataHandler);
  $('input[name="dataRadioOptions"]').on("change", viewWorkerDataHandler);

  // Approves/rejects/bonuses the currently selected assignment
  $("#bonus-autoToggle").on("click", () => {
    if ($("#bonus-autoToggle").hasClass("active")) {
      $("#bonus-autoToggle").removeClass("active");
      bonusInfoChanged();
      $("#bonus-value").prop("disabled", false);
    } else {
      $("#bonus-autoToggle").addClass("active");
      bonusInfoChanged();
      $("#bonus-value").prop("disabled", true);
    }
  });

  // Input listeners
  $("#bonus-value").on("change", bonusInfoChanged);
  $("#bonus-file").on("change", handleBonusFileUpload);

  // Button listeners
  $("#approveOne").on("click", approveIndividualHandler);
  $("#rejectOne").on("click", rejectIndividualHandler);
  $("#bonusOne").on("click", bonusOneWorkerModal);
  $("#approval-submit").on("click", approveAllHandler);
  $("#bonus-submit").on("click", bonusAllHandler);

  // Approves/bonuses all the workers in the database showing
  $("#approveAll").on("click", approveWorkersModal);
  $("#bonusAll").on("click", bonusWorkersModal);

  // Set up the batch download button on local
  if (HIT_LOCAL) {
    $("#downloadOneDataHref").attr(
      "href",
      "/api/assignments/action/datadownload?assignmentid=" +
        data["assignmentId"]
    );
  }
});