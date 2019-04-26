let searchArticle = document.querySelector("#searchArticle");
let myArticles = document.querySelector("#myArticles");
searchArticle.addEventListener("keyup", function(event) {
    let value = this.value.toLowerCase();
    for (let article of myArticles.children) {
        articleContent = article.textContent.toLowerCase()
        if (!articleContent.includes(value)) article.style.display = "none"
        else article.style.display = ""
    }
});