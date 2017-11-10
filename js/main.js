// Hides the element with the given ID
// Shows the element with the next highest ID

var choices = [];
var responseTimes = [];
var currentPageID = 0;
  var currentResponseTime = 0;

function handleKeyPress(event) {
  // Handle either the "1" or "2" buttons.
  // More can be added.
  // TODO: limit to number of choices available on screen.
  if (event.keyCode == 49) {
    recordChoiceAndAdvanceToNext(0);
  } else if (event.keyCode == 50) {
    recordChoiceAndAdvanceToNext(1);
  }
}


function submitChoicesAndTimes(formID, choiceInputID, timeInputID) {
  var choiceInput = document.getElementById(choiceInputID);
  if (choiceInput != null) {
    choiceInput.value = JSON.stringify(choices);
  }

  var timeInput = document.getElementById(timeInputID);
  if (timeInput != null) {
    timeInput.value = JSON.stringify(responseTimes);
  }

  var form = document.getElementById(formID);
  if (form != null) {
    form.submit();
  }
}


function recordChoiceAndAdvanceToNext(choiceID) {
  // TODO: end timer
  currentResponseTime = 100;
  choices.push(choiceID);
  responseTimes.push(currentResponseTime);
  advanceToNext();
}


function advanceToNext() {
  var currentElement = document.getElementById(currentPageID);
  if (currentElement == null) {
    throw "no element with given ID";
  }

  nextPageID = currentPageID + 1;
  var nextElement = document.getElementById(nextPageID);
  if (nextElement == null) {
    throw "no element with incremented ID";
  }

  currentElement.style.display = "none";
  nextElement.style.display = "table-cell";

  currentPageID = nextPageID;

  // Clear the previous response time
  currentResponseTime = 0;

  var audios = nextElement.getElementsByTagName("audio");
  if (audios.length == 0) {
    // no audio on page I guess
    return;
  }

  if (audios.length > 1) {
    throw "too many audio files in one section"
  }

  var audio = audios[0];
  audio.play();

  // TODO: begin timer

  // TODO: do not allow interaction until audio has finished playing
}
