$(document).ready(function(){
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('#topBtn').fadeIn();
        } else {
            $('#topBtn').fadeOut();
        }
    });
    $('#topBtn').click(function(){
        $("html, body").animate({ scrollTop: 0 }, 500);
        return false;
    });
    $('#scroller').click(function(){
        $('html, body').animate({
        scrollTop: $('#benefits').offset().top
        },500)
    });
});
$("#accordion").on("hide.bs.collapse show.bs.collapse", e => {
  $(e.target)
    .prev()
    .find("i:last-child")
    .toggleClass("fa-minus fa-plus");
});