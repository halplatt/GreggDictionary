
function findIdx(input,arrName) {
    var i
    for (i = 0; i < arrName.length; i++) 
        {
            if (arrName[i].toLowerCase() > input.toLowerCase()) {break}
        }
    if (i>0){i--}
    return arrName[i]
}

function findNum(input,arrName) {
    var i
    for (i = 0; i < arrName.length; i++) 
        {
            if (arrName[i].toLowerCase() > input.toLowerCase()) {break}
        }
if (i==0){i++}
    return i
}


function refreshImage() {
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsWord);
	var path = '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshName() {
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Proper Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsName);
	var path = '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshPhrase() {
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordNum = findNum(word,djsPhrase);
	var path = '<img src="djsDictionary/';
	path = path.concat('djsPhrase ','(',wordNum,')', '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshCenWord() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenWord);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}


 
function refreshCenBrief() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Brief Forms)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenBrief);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshCenPhrase() {
	hideSuggestion() 
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenPhrase);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
 
function refreshCenWomen() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Women Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenWomen);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenMen() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Men Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenMen);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenSur() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Sur Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenSur);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenUSName() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (US City Names)";

	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenUSName);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenGeoName() {
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Geographical Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenGeoName);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshSimWord() {
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,simWord);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshSimName() {
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand (Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,simName);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshPreWord() {
	hideSuggestion()
	loadAboutPre()
	document.getElementById('gsdTitle').innerHTML = "Gregg Pre-Anniversary Shorthand (1916)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,preWord);
	var path = '<img src="preDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}

function loadAboutDJS() {
	var aboutText = "";
	aboutText = aboutText.concat("<p><b>Page from</b> <i>Gregg Shorthand Dictionary DJS,</i> a book published by The McGraw-Hill Publishing Company in 1963, written by Charles Rader. </p>");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutCen() {
	var aboutText = "";
	aboutText = aboutText.concat("<p><b>Page from</b> <i>Gregg Shorthand Dictionary Centennial Edition Abridged,</i> a book published by The McGraw-Hill Publishing Company in 1989, written by Charles E. Zoubek, Gregg Condon. </p>");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutSim() {
	var aboutText = "";
	aboutText = aboutText.concat("<p><b>Page from</b> <i>Gregg Shorthand Dictionary Simplified,</i> a book published by The Gregg Publishing Company in 1945, written by Charles Rader. </p>");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutPre() {
	var aboutText = "";
	aboutText = aboutText.concat("<p><i><b>Page from</b> Gregg Shorthand Dictionary (1916),</i> a book published by The Gregg Publishing Company in 1916, including 17,000 shorthand forms written by Alice Rinne Hagar. A <a href=\"https://greggshorthand.github.io/gsd1916.pdf\" target=\"_blank\">pdf version</a> dictionary can be found on <a href=\"https://greggshorthand.github.io\" target=\"_blank\">this site</a>.</p>");

	document.getElementById('about').innerHTML = aboutText;
}
