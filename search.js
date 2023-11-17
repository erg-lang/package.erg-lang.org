window.document.onkeydown = function (event) {
    if (event.key == "Enter" && document.activeElement.id == "search-input") {
        event.preventDefault();
        search();
    }
};

function getParam(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function getSearchQuery() {
    return getParam("search");
}

let input = document.getElementById("search-input");
input.value = getSearchQuery();

let options = {
    valueNames: ["package-name", "package-description"]
}
let packageList = new List("package-list", options);

function search() {
    let page_title = document.getElementById("page-title");
    if (input.value != "") {
        page_title.innerHTML = `Search Results for "${input.value}"`;
    } else {
        page_title.innerHTML = "All Packages";
    }
    let res = packageList.search(input.value);
    let counter = document.getElementById("result-counter");
    counter.innerHTML = "found " + res.length + " packages";
}

search();
