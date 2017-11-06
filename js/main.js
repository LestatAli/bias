// Hides the element with the given ID
// Shows the element with the next highest ID

var choices = [];

function submitChoices(formID, inputID) {
  var input = document.getElementById(inputID);
  if (input != null) {
    input.value = JSON.stringify(choices);
  }

  var form = document.getElementById(formID);
  if (form != null) {
    form.submit();
  }
}

function recordChoiceAndAdvanceToNext(choiceID, currentPageID) {
  choices.push(choiceID);
  advanceToNext(currentPageID);
}

function advanceToNext(currentPageID) {
  if (currentPageID !== parseInt(currentPageID, 10)) {
    throw "currentID is not an integer"
  }

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

  // TODO: do not allow interaction until audio has finished playing
}
