//v2025.0820.0300pm display image above page
//v2025.0615.0553pm public-domain-only=pd hide link to andrew owen's
//v2025.0611.0339pm add style="width:60%" to page images
//v2025.0526.0350pm add annPhrase button
//v2025.0521.0745pm add S90Word button
//v2025.0506.0240pm pageCntAdj to not exceed the length of the array
// v2025.0505.1000pm persist last button clicked in local storage.
// v2025.0505.0300pm to verify word is in the djsWords arry before displaying Outline.
// v2025.0504.1252pm to add version number to JS
// updated 1/15/2025 at 9:42 rename refeshImage to refreshDjsWord,refrshPhrase to refreshDjsPhrase, refrshName to refreshDjsName
//updated 1/15/2025 at 2:27 to set lastButton to hold the last button clicked;
function getdjsJSVersion() {
    return 'djs.js v2025.0820.0300pm';
}
// Declare global variables for clarity
var public_domain_only = typeof public_domain_only !== 'undefined' ? public_domain_only : '';
// Declare global variable
let simReferencejson = [];

// Function to load JSON and assign to global variable
function loadsimReferencejson() {
    fetch('./simDictionary/!reference.json')
        .then(response => response.json())
        .then(data => {
            simReferencejson = data; // Now available globally
            // You can call other functions here if needed
        })
        .catch(error => {
            console.error('Error loading reference data:', error);
        });
}

// Run after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadsimReferencejson();
});
function findPageByWord(searchValue) {
	const regex = new RegExp('^'+searchValue+'$', 'i');
    for (const page of simReferencejson) {
        for (const word of page.words) {
            if (regex.test(word.t)) {
                // Return the page object and the matching word object
                return {
                    page: page.page,
                    word: word.t,
                    x: word.x,
                    y: word.y
                };
            }
        }
    }
    return null; // Not found
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
        if (num >= arrayName.length - 1) { num = arrayName.length - 1; }
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat('djsPhrase ','(',wordNum,')', '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}



function refreshS90Word(cntAdj) {
	setLastButton('refreshS90Word');
	pageCntAdj(cntAdj, s90Word);
	hideSuggestion()
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90Word);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshS90Phrase(cntAdj) {
	setLastButton('refreshS90Phrase');
	pageCntAdj(cntAdj, s90Phrase);
	hideSuggestion() 
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90Phrase);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
 
function refreshS90Women(cntAdj) {
	setLastButton('refreshS90Women');
	pageCntAdj(cntAdj, s90Women);
	hideSuggestion()
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (Women Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90Women);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshS90Men(cntAdj) {
	setLastButton('refreshS90Men');
	pageCntAdj(cntAdj, s90Men);
	hideSuggestion()
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (Men Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90Men);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshS90Sur(cntAdj) {
	setLastButton('refreshS90Sur');
	pageCntAdj(cntAdj, s90Sur);
	hideSuggestion()
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (Sur Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90Sur);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshS90USName(cntAdj) {
	setLastButton('refreshS90USName');
	pageCntAdj(cntAdj, s90USName);
	hideSuggestion()
	loadAboutS90()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (US City Names)";

	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90USName);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshS90GeoName(cntAdj) {
	setLastButton('refreshS90GeoName');
	pageCntAdj(cntAdj, s90GeoName);
	hideSuggestion()
	loadAboutCen()
	document.getElementById('gsdTitle').innerHTML = "Gregg Series 90 Shorthand (Geographical Names)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,s90GeoName);
	var path = '<img src="s90Dictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
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
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshSimWord(cntAdj) {
	setLastButton('refreshSimWord');
	pageCntAdj(cntAdj, simWord);
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand";
	var word = document.getElementById('txt1').value;
    // create a thumbnail image for the word
	document.getElementById('record').innerHTML = ""
	const result = findPageByWord(word);
	if (result) {
		const imageContainer = document.createElement('div');
		const DISPLAY_SIZE_SMALL = { x: 365, y: 100, offset: 5 };
        const DISPLAY_SIZE_LARGE = { x: 450, y: 180, offset: 10 };
        const IMG_WIDTH = 1281;
		imageContainer.className = 'relative overflow-hidden border';
		imageContainer.style.width = `${DISPLAY_SIZE_SMALL.x}px`;
		imageContainer.style.height = `${DISPLAY_SIZE_SMALL.y}px`;
		const img = document.createElement('img');
		img.className = 'absolute max-w-none';
		img.src = `./simDictionary/${result.page}.png`;
		img.alt = `Gregg shorthand for word: ${result.t}`;
		img.style.top = `-${result.y-25}px`; // Adjust to center the word vertically
		img.style.left = `-${result.x}px`; // Adjust to center the word horizontally
		img.style.width = '1281px'; // Assuming the image width is fixed
		imageContainer.appendChild(img);
		document.getElementById('record').appendChild(imageContainer);
	}


	var wordId = findIdx(word,simWord);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML += path;
}
function refreshSimName(cntAdj) {
	setLastButton('refreshSimName');
	pageCntAdj(cntAdj, simName);
	hideSuggestion()
	loadAboutSim()
	document.getElementById('gsdTitle').innerHTML = "Gregg Simplified Shorthand (Names)";
	var word = document.getElementById('txt1').value;

	// create a thumbnail image for the word
	document.getElementById('record').innerHTML = ""
	const result = findPageByWord(word);
	if (result) {
		const imageContainer = document.createElement('div');
		const DISPLAY_SIZE_SMALL = { x: 365, y: 100, offset: 5 };
        const DISPLAY_SIZE_LARGE = { x: 450, y: 180, offset: 10 };
        const IMG_WIDTH = 1281;
		imageContainer.className = 'relative overflow-hidden border';
		imageContainer.style.width = `${DISPLAY_SIZE_SMALL.x}px`;
		imageContainer.style.height = `${DISPLAY_SIZE_SMALL.y}px`;
		const img = document.createElement('img');
		img.className = 'absolute max-w-none';
		img.src = `./simDictionary/${result.page}.png`;
		img.alt = `Gregg shorthand for word: ${result.t}`;
		img.style.top = `-${result.y-25}px`; // Adjust to center the word vertically
		img.style.left = `-${result.x}px`; // Adjust to center the word horizontally
		img.style.width = '1281px'; // Assuming the image width is fixed
		imageContainer.appendChild(img);
		document.getElementById('record').appendChild(imageContainer);
	}



	var wordId = findIdx(word,simName);
	var path = '<img src="simDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML += path;
}
function refreshAnnPhrase(cntAdj) {
	setLastButton('refreshAnnPhrase');
	pageCntAdj(cntAdj, annPhrase);
	hideSuggestion() 
	loadAboutAnnPhrase()
	document.getElementById('gsdTitle').innerHTML = "Gregg Anniversary Shorthand (Phrases)";
	var word = document.getElementById('txt1').value;
	var wordId = findIdx(word,annPhrase);
	var path = '<img src="annDictionary/';
	path = path.concat(wordId, '.png" style="width:60%">');
	document.getElementById('record').innerHTML = path;
}
function refreshPreWord(cntAdj) {
	setLastButton('refreshPreWord');
	pageCntAdj(cntAdj, preWord);
	hideSuggestion()
	loadAboutAnn()
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
	aboutText = aboutText.concat("<b>Page from</b> <i>Gregg Shorthand Dictionary DJS,</i> a book published by The McGraw-Hill Publishing Company in 1963, written by Charles Rader.");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutS90() {
	var aboutText = "";
	aboutText = aboutText.concat("<b>Page from</b> <i>Gregg Shorthand Dictionary Series 90,</i> a book published by The McGraw-Hill Publishing Company in 1978, written by Charles Rader.");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutCen() {
	var aboutText = "";
	aboutText = aboutText.concat("<b>Page from</b> <i>Gregg Shorthand Dictionary Centennial Edition Abridged,</i> a book published by The McGraw-Hill Publishing Company in 1989, written by Charles E. Zoubek, Gregg Condon.");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutSim() {
	var aboutText = "";
	aboutText = aboutText.concat("<b>Page from</b> <i>Gregg Shorthand Dictionary Simplified,</i> a book published by The Gregg Publishing Company in 1945, written by Charles Rader. ");
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutAnnPhrase() {
	var aboutText = "";
	aboutText = aboutText.concat("<b>Page from</b> <i>Gregg Shorthand Phrase Book (1930),</i> a book published by The Gregg Publishing Company in 1930, forms written by Harriet M. Johnson.");
	if (public_domain_only == '') {
		aboutText = aboutText.concat(" A <a href=\"./annDictionary/AnnPhrasebook.pdf\" target=\"_blank\">pdf version here</a>.");
	}
	document.getElementById('about').innerHTML = aboutText;
}
function loadAboutPre() {
	var aboutText = "";
	aboutText = aboutText.concat("<i><b>Page from</b> Gregg Shorthand Dictionary (1916),</i> a book published by The Gregg Publishing Company in 1916, including 17,000 shorthand forms written by Alice Rinne Hagar.");
	if (public_domain_only == '') {
		aboutText = aboutText.concat(" A <a href=\"https://greggshorthand.github.io/gsd.pdf\" target=\"_blank\">pdf version</a> dictionary can be found on <a href=\"https://greggshorthand.github.io\" target=\"_blank\">this site</a>.");
	}
	document.getElementById('about').innerHTML = aboutText;
}

