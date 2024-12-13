// 20231216 convert to use Array
// Add an event listener for the keydown event
document.addEventListener("keydown", function(event) {
    // Check if the key pressed is enter
    if (event.key === "Enter") {
      // Call the displayHello function
      performSearch();
    }
  });

  //add vertical align to the image based on the content of a corresponding text file 
  function getVerticalAlign(pngFile) {
    var txtFile = pngFile.replace('.png', '.txt');

    return fetch(txtFile)
        .then(response => {
            if (!response.ok) {
                return '0px';
            }
            return response.text();
        })
        .then(px => '-' + px.trim() + 'px')  // Prepend a '-' to the number
        .catch(() => '0px');
}

// Function to perform the search
function performSearch() {
    const regexInput = document.getElementById("regexInput");
    const resultList = document.getElementById("resultList");
    const pattern = regexInput.value;
    
    // Clear previous results
    resultList.innerHTML = "";

    try {
        // Escape the user input and create the regular expression
        dict.forEach(word => {
            const regexPattern = new RegExp(pattern, 'i');
            if (regexPattern.test(word)) {
                const listItem = document.createElement("li");
                listItem.textContent = word;
                listItem.addEventListener("click", () => copyToClipboard(word));

                // Create an img element for the word if the PNG file exists
                const img = document.createElement("img");
                img.src = `/djsWords/${word}.png`;
                img.onerror = function() {
                    this.style.display = "none";  // Hide the image if it fails to load
                };

                // Add vertical align to the image based on the content of a corresponding text file
                getVerticalAlign(img.src).then(verticalAlign => {
                    img.style.verticalAlign = verticalAlign;
                });

                listItem.appendChild(img);

                // Create an img element for the text image
                const img2 = document.createElement("img");
                img2.src = `/djsWords/${word}.tag.png`;
                img2.onerror = function() {
                    this.style.display = "none";  // Hide the image if it fails to load
                };

                listItem.appendChild(img2);

                resultList.appendChild(listItem);
            }
        });
    } catch (error) {
        // Handle the error by displaying an alert
        alert(`Regular Expression ${pattern} Error: ${error.message}`);
    }

    // After looping through dict
    if (resultList.innerHTML === "") {
        const noResults = document.createElement("li");
        noResults.textContent = "No results found";
        resultList.appendChild(noResults);
    }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    const clipboardInput = document.getElementById("clipboardInput");
    clipboardInput.value = text;
    clipboardInput.select();
    document.execCommand("copy");
    clipboardInput.value = "";
    openInNewTab(text)
}

//Function to open in new tab
function openInNewTab(text) {
    url='djshorthand.html?x='+text
    var newTab = window.open('', 'DJshorthand');

    // This part is executed in the context of the newly opened window/tab.
    if (newTab.location.href === "about:blank") {
        // If the tab is new and hasn't loaded any page yet, load our URL
        newTab.location.href = url;
    } else {
        // If the tab already has content, refresh with the new URL
        newTab.location.replace(url);
    }

    // Bring the tab to front
    newTab.focus();
 
};


// Attach the search function to the button click event
const searchButton = document.getElementById("searchButton");
searchButton.addEventListener("click", performSearch);



