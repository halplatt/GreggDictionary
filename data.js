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

function hideSuggestion() {
	document.getElementById("suggest").style.display="none";
}

function refreshImage() {
	var word = document.getElementById('txt1').value.toLowerCase();
	var order = findOrder(word);
	var order_reverse = findOrderReverse(word);
	var path = '<img src="dataword/';
	if (order >= 0) {
		path = path.concat(word.toString(), '.png">');
	} else {
		path = "<p>Sorry, the word '";
		path = path.concat(word, "' is not collected in <i>Gregg Shorthand Dictionary.</i></p>");
		var starting = -order - 3;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict[starting + i];
			document.getElementById('bt'.concat(i.toString())).value = thisWord;
			imgpath = '<img src="dataword/'+thisWord+'.png">';
			document.getElementById('sh'.concat(i.toString())).innerHTML  = imgpath;
		}
		starting = -order_reverse - 3;
		if (starting < 0) starting = 0;
		if (starting > 18663) starting = 18663;
		for (i = 0; i < 4; i++) {
			var thisWord = dict_reverse[starting + i].split("").reverse().join("");
			document.getElementById('bt'.concat((i + 4).toString())).value = thisWord;
			imgpath = '<img src="dataword/'+thisWord+'.png">';
			document.getElementById('sh'.concat((i + 4).toString())).innerHTML = imgpath;
		}
		document.getElementById("suggest").style.display="inline";
	}
	document.getElementById('record').innerHTML = path;
}

function loadAbout() {
	var aboutText = "<h2>About</h2>";
	aboutText = aboutText.concat("<p><i>Gregg Shorthand Dictionary</i> is a book published by The Gregg Publishing Company in 1930, including 18667 shorthand plates written by Winifred Kenna Richmond. A <a href=\"http://gregg.angelfishy.net/gsd.pdf\">pdf version</a> dictionary can be found on <a href=\"http://gregg.angelfishy.net\">this site</a>.</p><p>I extracted all the writings in this dictionary and made this website for easier search on computers and mobile devices.</p>");
	document.getElementById('record').innerHTML = aboutText;
}
