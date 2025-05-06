// v2025.0505.1000pm persist last button clicked in local storage.
// v2025.0505.0300pm to verify word is in the djsWords arry before displaying Outline.
// v2025.0504.1252pm to add version number to JS
// updated 1/15/2025 at 9:42 rename refeshImage to refreshDjsWord,refrshPhrase to refreshDjsPhrase, refrshName to refreshDjsName
//updated 1/15/2025 at 2:27 to set lastButton to hold the last button clicked;
function getdjsJSVersion() {
    return 'djs.js v2025.0505.1000pm';
}
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
function buildWordImg(word) {
    const regexPattern = new RegExp(`^${word}$`, 'i'); // Match the full word exactly (case-insensitive)
    const verifiedWord=dict.find(entry => regexPattern.test(entry)); // Returns the first case-sensitive match
	if (verifiedWord === undefined) {//word not in the array
		return `<p style="text-align: center;">Outline for ${word} not in the DJS image collection.</p>`;
	} else {//word is in the array
		return `<img src="djsWords/${verifiedWord}.png" title="${verifiedWord}" alt="${verifiedWord}" onerror="this.outerHTML='<span>Outline for ${verifiedWord} not available</span>'"><br>`;
	}
}

function refreshDjsWord(cntAdj) {
	setLastButton('refreshDjsWord')
	pageCntAdj(cntAdj, djsWord);
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsWord);
	var path = buildWordImg(word)
	path += '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshDjsName(cntAdj) {
	setLastButton('refreshDjsName')
	pageCntAdj(cntAdj, pageCntAdj(cntAdj, djsName));
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Proper Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,djsName);
	var path = buildWordImg(word)
	path += '<img src="djsDictionary/';
	path = path.concat(wordId, '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshDjsPhrase(cntAdj) {
	setLastButton('refreshDjsPhrase');
	pageCntAdj(cntAdj, djsPhrase);
	hideSuggestion()
	loadAboutDJS()
	document.getElementById('gsdTitle').innerHTML = "Gregg Diamond Jubilee Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordNum = findNum(word,djsPhrase);
	var path = buildWordImg(word)
	path += '<img src="djsDictionary/';
	path = path.concat('djsPhrase ','(',wordNum,')', '.png">');
	document.getElementById('record').innerHTML = path;
}

function refreshCenWord(cntAdj) {
	setLastButton('refreshCenWord');
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
	setLastButton('refreshCenBrief');
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
	setLastButton('refreshCenPhrase');
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
	setLastButton('refreshCenWomen');
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
	setLastButton('refreshCenMen');
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
	setLastButton('refreshCenSur');
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
	setLastButton('refreshCenUSName');
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
	setLastButton('refreshCenGeoName');
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
	setLastButton('refreshSimWord');
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
	setLastButton('refreshSimName');
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
	setLastButton('refreshPreWord');
	pageCntAdj(cntAdj, preWord);
	hideSuggestion()
	loadAboutPre()
	document.getElementById('gsdTitle').innerHTML = "Gregg Pre-Anniversary Shorthand (1916)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,preWord);
	var path = '<img src="preWords/' + word + '.png" title="' + word + '" alt="' + word + '" onerror="this.outerHTML=\'<span>Outline not available</span>\'"><br>';
	path += '<img src="preDictionary/';
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
