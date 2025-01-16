//updated 1/15/2025 at 9:42 rename refeshImage to refreshDjsWord,refrshPhrase to refreshDjsPhrase, refrshName to refreshDjsName
//updated 1/15/2025 at 2:27 to set lastButton to hold the last button clicked;
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
// Generic function to handle page forward or back adjustment
function pageCntAdj(cntAdj, arrayName) {
	if (typeof cntAdj !== 'undefined' && !isNaN(cntAdj)) {
        let word = document.getElementById('txt1').value;
        let num = findNum(word, arrayName);
        num = --num + cntAdj; // Adjust for page forward or back and commpensate for 0 based array
        if (num < 0) { num = 0; }
        if (num >= arrayName.length) { num = arrayName.length - 1; }
        document.getElementById('txt1').value = arrayName[num];
    }
}



function refreshDjsWord(cntAdj) {
	lastButton = 'refreshDjsWord';
	pageCntAdj(cntAdj, djsWord);
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsWord);
	var path = '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshDjsName(cntAdj) {
	lastButton = 'refreshDjsName';
	pageCntAdj(cntAdj, pageCntAdj(cntAdj, djsName));
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Proper Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsName);
	var path = '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshDjsPhrase(cntAdj) {
	lastButton = 'refreshDjsPhrase';
	pageCntAdj(cntAdj, djsPhrase);
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordNum = findNum(word,djsPhrase);
	var path = '<img src="djsDictionary/';
	path = path.concat('djsPhrase ','(',wordNum,')', '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshCenWord(cntAdj) {
	lastButton = 'refreshCenWord';
	pageCntAdj(cntAdj, cenWord);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenWord);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}



 
function refreshCenBrief(cntAdj) {
	lastButton = 'refreshCenBrief';
	pageCntAdj(cntAdj, cenBrief);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Brief Forms)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenBrief);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshCenPhrase(cntAdj) {
	lastButton = 'refreshCenPhrase';
	pageCntAdj(cntAdj, cenPhrase);
	hideSuggestion() 
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenPhrase);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
 
function refreshCenWomen(cntAdj) {
	lastButton = 'refreshCenWomen';
	pageCntAdj(cntAdj, cenWomen);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Women Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenWomen);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenMen(cntAdj) {
	lastButton = 'refreshCenMen';
	pageCntAdj(cntAdj, cenMen);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Men Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenMen);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenSur(cntAdj) {
	lastButton = 'refreshCenSur';
	pageCntAdj(cntAdj, cenSur);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Sur Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenSur);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenUSName(cntAdj) {
	lastButton = 'refreshCenUSName';
	pageCntAdj(cntAdj, cenUSName);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (US City Names)";

	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenUSName);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshCenGeoName(cntAdj) {
	lastButton = 'refreshCenGeoName';
	pageCntAdj(cntAdj, cenGeoName);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Centennial Shorthand (Geographical Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,cenGeoName);
	var path = '<img src="cenDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}
function refreshSimWord(cntAdj) {
	lastButton = 'refreshSimWord';
	pageCntAdj(cntAdj, simWord);
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,simWord);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshSimName(cntAdj) {
	lastButton = 'refreshSimName';
	pageCntAdj(cntAdj, simName);
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand (Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,simName);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshPreWord(cntAdj) {
	lastButton = 'refreshPreWord';
	pageCntAdj(cntAdj, preWord);
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
