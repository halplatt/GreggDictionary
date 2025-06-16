// ann.js v2025.0523.0746pm  adjust styling on suggestions.
// v2025.0615.0553pm public-domain-only=pd hide link to andrew owen's
// v2025.0506.0104pm fix error in search.
// v2025.0505.1000pm persist last button clicked in local storage.
//v22025.0505.0200pm dataset.ann.js now contains ann_dict and ann_dict_reverse arrays. Modified code to reflet this change.
//updated 5/4/2025 12:52pm to add a new function to find the page number of a word in the dictionary and display it in the record area
//updated 1/15/2025 2:27 to set lastButton = 'refreshAnnWord';

// Declare global variables for clarity
var public_domain_only = typeof public_domain_only !== 'undefined' ? public_domain_only : '';

function getannJSVersion() {
	return 'ann.js v2025.0615.0553pm';
}
function findOrder(input) {
	var left = 0;
	var right = ann_dict.length - 1; // Dynamically set the right boundary
	var center;
	var comp;
	let compLeft, compRight;
	input = input.toLowerCase();
	while (right - left > 1) {
		center = Math.ceil((left + right) / 2);
		comp = input.localeCompare(ann_dict[center].toLowerCase());
		if (comp == 0) return center;
		if (comp < 0) right = center;
		if (comp > 0) left = center;
	}
	compLeft = input.localeCompare(ann_dict[left].toLowerCase());
	compRight = input.localeCompare(ann_dict[right].toLowerCase());
	if (compLeft == 0) return left;
	if (compRight == 0) return right;
	if (compLeft < 0) return -left - 1;
	if (compLeft > 0 && compRight < 0) return -left - 2;
	if (compRight > 0) return -left - 3;
}

function findOrderReverse(input) {
	var left = 0;
	var right = ann_dict_reverse.length - 1; // Dynamically set the right boundary
	var center;
	var comp;
	let compLeft, compRight;
	var input_reverse = input.toLowerCase().split("").reverse().join("");
	while (right - left > 1) {
		center = Math.ceil((left + right) / 2);
		comp = input_reverse.localeCompare(ann_dict_reverse[center].toLowerCase());
		if (comp == 0) return center;
		if (comp < 0) right = center;
		if (comp > 0) left = center;
	}
	compLeft = input_reverse.localeCompare(ann_dict_reverse[left].toLowerCase());
	compRight = input_reverse.localeCompare(ann_dict_reverse[right].toLowerCase());
	if (compLeft == 0) return left;
	if (compRight == 0) return right;
	if (compLeft < 0) return -left - 1;
	if (compLeft > 0 && compRight < 0) return -left - 2;
	if (compRight > 0) return -left - 3;
}
async function fetchData() {
	const response = await fetch('annDictionary/!reference.json');
	const annMap = await response.json();
	return annMap;
}

async function findPageObj(testWord) {
	const data = await fetchData();
	for (const page of data) {
		for (const word of page.words) {
			if (testWord.toLowerCase() === word.t.toLowerCase()) {
				return page;
			}
		}
	}
	return null; // Return null if no match is found
}

async function refreshAnnWord(cntAdj) {
	setLastButton('refreshAnnWord');
	hideSuggestion();
	loadAboutAnn();
	document.getElementById('gsdTitle').innerHTML = "Gregg Anniversary Shorthand";
	// Adjust for page forward or back
	if (typeof cntAdj !== 'undefined' && !isNaN(cntAdj)) {
		let word = document.getElementById('txt1').value;
		let num = findNum(word, ann_dict);
		num--
		num += cntAdj;
		if (num < 0) { num = 0; }
		if (num >= ann_dict.length - 1) { num = ann_dict.length - 1; }
		document.getElementById('txt1').value = ann_dict[num];
	}
	var word = document.getElementById('txt1').value.toLowerCase();
	var order = findOrder(word);
	var order_reverse = findOrderReverse(word);
	var path = '<img src="annWords/';
	if (order >= 0) { //If word is found order is positive
		var pageObj = await findPageObj(word.toString()); // Use await here
        if (pageObj !== null) {
			path = '<img src="annWords/' + word + '.png">'
			path += '<img src="annDictionary/';
			path = path.concat(pageObj.page.toString(), '.png" style="max-width: 60%; display: block; margin: 10px auto;">');
        } else {
            path = "<p>Sorry, the page number for the word could not be found.</p>";
        }
		//11/22/2020 Logic below adds suggestions
		var starting = order - 1;
		if (starting < 0) starting = 0;
		if (starting > ann_dict.length-4) starting = ann_dict.length-5; 
		for (let i = 0; i < 4; i++) {
			var thisWord = ann_dict[starting + i];
			document.getElementById('bt'.concat(i.toString())).value = thisWord;
			imgpath = '<img src="annWords/'+thisWord+'.png">';
			document.getElementById('sh'.concat(i.toString())).innerHTML  = imgpath;
		}
		starting = order_reverse - 1;
		if (starting < 0) starting = 0;
		if (starting > ann_dict_reverse.length-4) starting = ann_dict_reverse.length-5;
		for (let i = 0; i < 4; i++) {
			var thisWord = ann_dict_reverse[starting + i].split("").reverse().join("");
			document.getElementById('bt'.concat((i + 4).toString())).value = thisWord;
			imgpath = '<img src="annWords/'+thisWord+'.png">';
			document.getElementById('sh'.concat((i + 4).toString())).innerHTML = imgpath;
		}
		document.getElementById("suggest").style.display="inline-block";
	} else {
		path = "<p>Sorry, the word '" + word + "' is not found in the <i>Gregg Anniversary Shorthand Dictionary.</i></p>";
		var starting = -order-4;
		if (starting < 0) starting = 0;
		if (starting > ann_dict.length-4) starting = ann_dict.length-4;
		for (let i = 0; i < 4; i++) {
			var thisWord = ann_dict[starting + i];
			document.getElementById('bt'.concat(i.toString())).value = thisWord;
			imgpath = '<img src="annWords/'+thisWord+'.png">';
			document.getElementById('sh'.concat(i.toString())).innerHTML  = imgpath;
		}
		starting = -order_reverse - 3;
		if (starting < 0) starting = 0;
		if (starting > ann_dict_reverse.length-4) starting = ann_dict_reverse.length-4;
		for (let i = 0; i < 4; i++) {
			var thisWord = ann_dict_reverse[starting + i].split("").reverse().join("");
			document.getElementById('bt'.concat((i + 4).toString())).value = thisWord;
			imgpath = '<img src="annWords/'+thisWord+'.png">';
			document.getElementById('sh'.concat((i + 4).toString())).innerHTML = imgpath;
		}
		document.getElementById("suggest").style.display="block";		
	}
	document.getElementById('record').innerHTML = path;
	
}

function loadAboutAnn() {
	var aboutText = "";
	aboutText = aboutText.concat("<i><b>image extracted from</b> Gregg Shorthand Dictionary,</i> a book published by The Gregg Publishing Company in 1930, including 18667 shorthand forms written by Winifred Kenna Richmond.");
	if (public_domain_only=='') {
		aboutText = aboutText.concat(" A <a href=\"https://greggshorthand.github.io/gsd.pdf\" target=\"_blank\">pdf version</a> dictionary can be found on <a href=\"https://greggshorthand.github.io\" target=\"_blank\">this site</a>.");
	}
	document.getElementById('about').innerHTML = aboutText;
}
