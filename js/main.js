// Hides the element with the given ID
// Shows the element with the next highest ID

function advanceToNext(currentID) {
  if (currentID !== parseInt(currentID, 10)) {
    throw "currentID is not an integer"
  }

  var currentElement = document.getElementById(currentID);
  if (currentElement == null) {
    throw "no element with given ID";
  }

  nextID = currentID + 1;
  var nextElement = document.getElementById(nextID);
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
