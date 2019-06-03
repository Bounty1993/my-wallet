let googleSearch = document.querySelector("#googleSearch");
let googleArticles = document.querySelector("#googleArticles");
googleSearch.addEventListener("keyup", function(event) {
    let value = this.value.toLowerCase();
    for (let article of googleArticles.children) {
        articleContent = article.textContent.toLowerCase()
        if (!articleContent.includes(value)) article.style.display = "none"
        else article.style.display = ""
    }
});
let yahooSearch = document.querySelector("#yahooSearch");
let yahooArticles = document.querySelector("#yahooArticles");
yahooSearch.addEventListener("keyup", function(event) {
    let value = this.value.toLowerCase();
    for (let article of yahooArticles.children) {
        articleContent = article.textContent.toLowerCase()
        if (!articleContent.includes(value)) article.style.display = "none"
        else article.style.display = ""
    }
});