// Hides the element with the given ID
// Shows the element with the next highest ID

var gResponses = [];
var gResponseTimes = [];
var gTimestamps = [];
var gCurrentPageID = 0;
var gCurrentResponseTime = 0;
var gCurrentTrialStartTime = 0;
var gIsAcceptingKeyPresses = true;


function begin() {
  _advanceToNextWithCompletion(0, function() {
    gCurrentTrialStartTime = Date.now();
    gIsAcceptingKeyPresses = true;
  });
}


function handleKeyPress(event) {
  if (gIsAcceptingKeyPresses) {

    gIsAcceptingKeyPresses = false;
    completion = function() {
        gIsAcceptingKeyPresses = true;
    }

    // Handle either the "[" or "/" buttons.
    if (event.keyCode == 91) {
      _recordResponseAndAdvanceToNextWithCompletion(0, completion)
    } else if (event.keyCode == 47) {
      _recordResponseAndAdvanceToNextWithCompletion(1, completion);
    } else {
      completion();
    }
  }
}


function _recordResponseAndAdvanceToNextWithCompletion(responseID, completion) {
  currentTimestamp = Date.now();
  gCurrentResponseTime = currentTimestamp - gCurrentTrialStartTime;
  gResponses.push(responseID);
  gResponseTimes.push(gCurrentResponseTime);
  gTimestamps.push(currentTimestamp);

  gCurrentResponseTime = 0;

  _advanceToNextWithCompletion(500, function() {
    gCurrentTrialStartTime = Date.now();
    completion();
  });
}


function _advanceToNextWithCompletion(delay, completion) {
  var currentElement = document.getElementById(gCurrentPageID);
  if (currentElement == null) {
    throw "no element with given ID";
  }

  nextPageID = gCurrentPageID + 1;
  var nextElement = document.getElementById(nextPageID);
  if (nextElement == null) {
    throw "no element with incremented ID";
  }

  // Hide the current page, next one loads after a delay
  currentElement.style.display = "none";

  gCurrentPageID = nextPageID;

  var audios = nextElement.getElementsByTagName("audio");
  if (audios.length == 0) {
    // no audio on page I guess
    nextElement.style.display = "table-cell";
    completion();
  } else {
    if (audios.length > 1) {
      throw "too many audio files in one section"
    }

    var audio = audios[0];

    setTimeout(function() {
      nextElement.style.display = "table-cell";
      audio.play();
      audio.addEventListener("ended", completion);
    }, delay);
  }
}

function submitResponsesAndTimes(formID, responseInputID, timeInputID, timestampInputID) {
  var responseInput = document.getElementById(responseInputID);
  if (responseInput != null) {
    responseInput.value = JSON.stringify(gResponses);
  }

  var timeInput = document.getElementById(timeInputID);
  if (timeInput != null) {
    timeInput.value = JSON.stringify(gResponseTimes);
  }

  var timestampInput = document.getElementById(timestampInputID);
  if (timestampInput != null) {
    timestampInput.value = JSON.stringify(gTimestamps);
  }

  var form = document.getElementById(formID);
  if (form != null) {
    form.submit();
  }
}
