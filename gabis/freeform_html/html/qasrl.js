<script language="javascript">

Array.prototype.contains = function(obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
};

Array.prototype.remove = function(obj) {
    var i = this.indexOf(obj);
    if (i > -1) {
        this.splice(i, 1);
    }
};

var black = "rgb(0, 0, 0)";
var gray = "rgb(64, 64, 64)";
var white = "rgb(255, 255, 255)";

var answer = document.getElementById("answer");
var checkedQuestions = [];
var checkedAnswers = [];
var checkedQuestionsHTML = document.getElementById("checked_questions");

function selectWord(element) {
    if (element.id.substring(0, 6) == "clone_") {
        // Ignore
    } else {
        var original = element;
        var me = parseInt(original.id);
        if ((original.style.color == black) || (original.style.color == "")) {
            if ((original.style.backgroundColor == white) || (original.style.backgroundColor == "")) {
                if (answer.hasChildNodes()) {
                    var start = cloneId(answer.firstChild);
                    var end = cloneId(answer.lastChild);
                    if (me < start) {
                        if (checkTokenRange(me, start-1)) {
                            for (var i = me; i < start; i++) {
                                doClone(i);
                            }
                        }
                    } else if (me > end) {
                        if (checkTokenRange(end+1, me)) {
                            for (var i = me; i > end; i--) {
                                doClone(i);
                            }
                        }
                    } else {
                        alert("This should not happen: " + me.toString() + " " + start.toString() + " " + end.toString());
                    }
                    sortClones();
                } else {
                    doClone(me);
                }
            } else {
                var start = cloneId(answer.firstChild);
                var end = cloneId(answer.lastChild);
                if ((me >= start) && (me <= end)) {
                    for (var i = me; i <= end; i++) {
                        undoClone(i);
                    }
                } else {
                    alert("This should not happen: " + me.toString() + " " + start.toString() + " " + end.toString());
                }
            }
        }
    }
}

function doClone(id) {
    var original = document.getElementById(id.toString());
    var clone = original.cloneNode(true);
    clone.id = "clone_" + original.id;
    clone.innerHTML = clone.innerHTML + " ";
    clone.style.fontWeight = "bold";
    answer.appendChild(clone);
    original.style.backgroundColor = "yellow";
}

function undoClone(id) {
    var original = document.getElementById(id.toString());
    if (original != null) {
        var clone = document.getElementById("clone_" + original.id);
        answer.removeChild(clone);
        original.style.backgroundColor = white;
    }
}

function sortClones() {
    var arr = [];
    for (var i = 0; i < answer.childNodes.length; i++) {
        arr.push(answer.childNodes[i]);
    }
    for (var i = 0; i < arr.length; i++) {
        answer.removeChild(arr[i]);
    }

    arr.sort(function(a, b) {
        var aid = cloneId(a);
        var bid = cloneId(b);
        return aid == bid ? 0 : (aid > bid ? 1 : -1);
    });

    for (var i = 0; i < arr.length; i++) {
        answer.appendChild(arr[i]);
    }
}

function cloneId(element) {
    return parseInt(element.id.substring(6));
}

function checkTokenRange(start, end) {
    for (var i = start; i <= end; i++) {
        var token = document.getElementById(i.toString());
        if (token == null) {
            return false;
        }
        if ((token.style.color != black) && (token.style.color != "")) {
            return false;
        }
    }
    return true;
}

function getQuestion() {
	var wh = document.getElementById("WH").value;
	var aux = document.getElementById("AUX").value;
	var ph1 = document.getElementById("PH1").value;
	var trg = document.getElementById("TRG").value;
	var ph2 = document.getElementById("PH2").value;
	var pp = document.getElementById("PP").value;
	var ph3 = document.getElementById("PH3").value;

    var question = [wh, aux, ph1, trg, ph2, pp, ph3];
    var empty = true;
    for (var i = 0; i < question.length; i++) {
        if (question[i] != "") {
            empty = false;
        }
    }
    if (empty) {
        return "EMPTY";
    }
    if ((wh == "") || (trg == "")) {
	    return "INVALID";
	}

	var question_str = wh;
	question = [aux, ph1, trg, ph2, pp, ph3];
	for (var i = 0; i < question.length; i++) {
	    if (question[i] != "") {
	        question_str += " " + question[i];
	    }
	}
	return question_str;
}

function resetQuestion() {
	document.getElementById("WH").value = "";
    document.getElementById("AUX").value = ""; 
	document.getElementById("PH1").value = ""; 
	document.getElementById("TRG").value = ""; 
	document.getElementById("PH2").value = ""; 
	document.getElementById("PP").value = ""; 
	document.getElementById("PH3").value = "";
}

function checkClick() {
    var question = getQuestion();
    if ((question == "EMPTY") || (question == "INVALID")) {
        alert("The question is invalid.");
        return;
    }
    if (answer.childNodes.length == 0) {
        alert("An answer must contain at least one token.");
        return;
    }

    var answerElements = [];
    for (var i = 0; i < answer.childNodes.length; i++) {
        if (answer.childNodes[i].nodeName == "SPAN") {
            answerElements.push(answer.childNodes[i]);
        }
    }

    var color = getColor(checkedQuestions.length);
    var selected = [];
    var newSentence = "";
    for (var i = 0; i < answerElements.length; i++) {
        var id = cloneId(answerElements[i]).toString();
        selected.push(id);
        newSentence = newSentence + answerElements[i].innerHTML;

        undoClone(cloneId(answerElements[i]));

        original = document.getElementById(id);
        original.style.backgroundColor = color;
        original.style.color = gray;
    }

    checkedQuestions.push(question);
    checkedAnswers.push(selected);
    document.getElementById("finito").value="Submit";
    
    //resetQuestion();
    checkedQuestionsHTML.innerHTML = '<span style="font-family: Calibri, Tahoma, Arial, sans-serif; font-size: 16px; font-style: italic;">' + question + '?</span> &nbsp; &nbsp;' + '<span style="background-color: ' + color + '">' + newSentence + '</span></br>' + checkedQuestionsHTML.innerHTML;
}

function getColor(i) {
    var red = 0;
    var green = 0;
    var blue = 0;

    var col1 = 255;
    var col2 = 208 - 16 * Math.floor(i / 6);
    var col3 = 160 - 48 * Math.floor(i / 6);

    switch (i % 6) {
        case 1:
            red = col1;
            green = col3;
            blue = col2;
            break;
        case 2:
            red = col3;
            green = col1;
            blue = col2;
            break;
        case 3:
            red = col1;
            green = col2;
            blue = col3;
            break;
        case 4:
            red = col3;
            green = col2;
            blue = col1;
            break;
        case 5:
            red = col2;
            green = col1;
            blue = col3;
            break;
        case 0:
            red = col2;
            green = col3;
            blue = col1;
            break;
    }

    red = getColorString(red);
    green = getColorString(green);
    blue = getColorString(blue);

    return "#" + red + green + blue;
}

function getColorString(color) {
    var s = color.toString(16);
    if (s.length == 1) {
        s = "0" + s;
    }
    return s;
}

function undoClick() {
	var minorUndo = false;
	if (answer.childNodes.length != 0) {
		var answerElements = [];
		for (var i = 0; i < answer.childNodes.length; i++) {
            if (answer.childNodes[i].nodeName == "SPAN") {
                answerElements.push(answer.childNodes[i]);
            }
		}
        for (var i = 0; i < answerElements.length; i++) {
            undoClone(cloneId(answerElements[i]));
        }
        minorUndo = true;
	}
	
	if (getQuestion() != "EMPTY"){
		resetQuestion();
		minorUndo = true;
	}
	
	if (!minorUndo){
        checkedQuestions.pop();
        if (checkedQuestions.length == 0){
        	document.getElementById("finito").value="I Can't ask about this word!";
        }

        var answerElements = checkedAnswers.pop();
        for (var i = 0; i < answerElements.length; i++) {
            var element = document.getElementById(answerElements[i]);
            element.style.backgroundColor = white;
            element.style.color = black;
        }

        var rollbackIndex = checkedQuestionsHTML.innerHTML.indexOf("br>") + 3;
        checkedQuestionsHTML.innerHTML = checkedQuestionsHTML.innerHTML.substring(rollbackIndex);
    }
}

function validateUnselected() {
    if (answer.childNodes.length != 0) {
        alert("You have not checked-in your current QA (check both question and answer).")
        return false;
    }

    if (checkedQuestions.length < 2) {
        var done = confirm("You have created " + checkedQuestions.length.toString() + " questions. Is that all?");
        if (!done) {
            return false;
        }
    }

    var questionsString = "";
    var answersTokenString = "";
    for (var i = 0; i < checkedQuestions.length; i++) {
        questionsString += checkedQuestions[i] + "?;";
        for (var j = 0; j < checkedAnswers[i].length; j++) {
            answersTokenString += checkedAnswers[i][j];
            answersTokenString += ",";
        }
        answersTokenString += ";";
    }

    var pred_index = document.getElementById("pred_index").value;
    document.getElementById("questions_str").value += pred_index + "|||" + questionsString + "|||";
    document.getElementById("answers_token_str").value += pred_index + "|||" + answersTokenString + "|||";

    return true;
}

window.onkeyup = function(event) {
    if (event.which == 32) { // Space-bar
        checkClick();
    } else if (event.ctrlKey && event.which == 90) { // Ctrl+Z
        undoClick();
    }
};

</script>