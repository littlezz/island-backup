/**
 * Created by zz on 10/1/16.
 */
function show_big(id){
    if (id.dataset.big == 0){
        id.style.width="auto";
        id.style.maxWidth="100%";
        id.dataset.big=1;
        id.style.cursor = 'zoom-out';
    }
    else {
        id.style.width="auto";
        id.style.maxWidth="25%";
        id.dataset.big=0;
        id.style.cursor = 'zoom-in';
    }
}