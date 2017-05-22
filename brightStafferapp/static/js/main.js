$(document).click(function (e) {
    var ele = $(e.toElement);
    console.log(e, ele[0].className)
    if (!ele.hasClass("hasDatepicker") && !ele.hasClass("ui-datepicker") && !ele.hasClass("ui-icon") && !$(ele).parent().parents(".ui-datepicker").length)
        $(".hasDatepicker").datepicker("hide");
});