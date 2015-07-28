/**
 * Created by @mani3 on 7/28/15.
 */
function selected(){
    var myselect = document.getElementById("selection_app");
    if (myselect.selectedIndex != 0) {
        var href = myselect.options[myselect.selectedIndex].value;
        location.href = href;
    }
}