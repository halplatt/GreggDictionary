function findOrder(input) {
	var left = 0;
	var right = 18666;
	var center = 9333;
	var comp;
	input = input.toLowerCase();
	while (right - left > 1) {
		center = Math.ceil((left + right) / 2);
		comp = input.localeCompare(dict[center].toLowerCase());
		if (comp == 0) return center;
		if (comp < 0) right = center;
		if (comp > 0) left = center;
	}
	compLeft = input.localeCompare(dict[left].toLowerCase());
	compRight = input.localeCompare(dict[right].toLowerCase());
	if (compLeft == 0) return left;
	if (compRight == 0) return right;
	if (compLeft < 0) return -left - 1;
	if (compLeft > 0 && compRight < 0) return -left - 2;
	if (compRight > 0) return -left - 3;
}

function findOrderReverse(input) {
	var left = 0;
	var right = 18666;
	var center = 9333;
	var comp;
	var input_reverse = input.toLowerCase().split("").reverse().join("");
	while (right - left > 1) {
		center = Math.ceil((left + right) / 2);
		comp = input_reverse.localeCompare(dict_reverse[center].toLowerCase());
		if (comp == 0) return center;
		if (comp < 0) right = center;
		if (comp > 0) left = center;
	}
	compLeft = input_reverse.localeCompare(dict_reverse[left].toLowerCase());
	compRight = input_reverse.localeCompare(dict_reverse[right].toLowerCase());
	if (compLeft == 0) return left;
	if (compRight == 0) return right;
	if (compLeft < 0) return -left - 1;
	if (compLeft > 0 && compRight < 0) return -left - 2;
	if (compRight > 0) return -left - 3;
}

function refreshAnnWord() {
	hideSuggestion()
	loadAboutAnn()
	document.getElementById('gsdTitle').innerHTML = "Gregg Anniversary Shorthand";
	var word = document.getElementById('txt1').value.toLowerCase();
	var order = findOrder(word);
	var order_reverse = findOrderReverse(word);
	var path = '<img src="annDictionary/';
	if (order >= 0) { //If word is found order is positive
		path = path.concat(word.toString(), '.png">');
		//11/22/2020 Logic below adds suggestions 
		var starting = order - 1;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict[starting + i];
			document.getElementById('bt'.concat(i.toString())).value = thisWord;
			imgpath = '<img src="annDictionary/'+thisWord+'.png">';
			document.getElementById('sh'.concat(i.toString())).innerHTML  = imgpath;
		}
		starting = order_reverse - 1;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict_reverse[starting + i].split("").reverse().join("");
			document.getElementById('bt'.concat((i + 4).toString())).value = thisWord;
			imgpath = '<img src="annDictionary/'+thisWord+'.png">';
			document.getElementById('sh'.concat((i + 4).toString())).innerHTML = imgpath;
		}
		document.getElementById("suggest").style.display="inline";
	} else {
		path = "<p>Sorry, the word '";
		path = path.concat(word, "' is not collected in <i>Gregg Shorthand Dictionary.</i></p>");
		var starting = -order - 3;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict[starting + i];
			document.getElementById('bt'.concat(i.toString())).value = thisWord;
			imgpath = '<img src="annDictionary/'+thisWord+'.png">';
			document.getElementById('sh'.concat(i.toString())).innerHTML  = imgpath;
		}
		starting = -order_reverse - 3;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict_reverse[starting + i].split("").reverse().join("");
			document.getElementById('bt'.concat((i + 4).toString())).value = thisWord;
			imgpath = '<img src="annDictionary/'+thisWord+'.png">';
			document.getElementById('sh'.concat((i + 4).toString())).innerHTML = imgpath;
		}
		document.getElementById("suggest").style.display="inline";
	}
	document.getElementById('record').innerHTML = path;
}

function loadAboutAnn() {
	var aboutText = "";
	aboutText = aboutText.concat("<p><i><b>image extracted from</b> Gregg Shorthand Dictionary,</i> a book published by The Gregg Publishing Company in 1930, including 18667 shorthand plates written by Winifred Kenna Richmond. A <a href=\"https://greggshorthand.github.io/gsd.pdf\" target=\"_blank\">pdf version</a> dictionary can be found on <a href=\"https://greggshorthand.github.io\" target=\"_blank\">this site</a>.</p>");
	document.getElementById('about').innerHTML = aboutText;
}
