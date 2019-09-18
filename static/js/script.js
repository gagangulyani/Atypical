$(document).ready(function() {
    $(".alert-dark").fadeTo(2000, 500).fadeOut(500, function() {
        $(".alert-dark").remove();
    });
});

// $(function() {
//     $('[data-toggle="tooltip"]').tooltip();
// })

function changeBG(src, _id, darkenbg = true) {
    _id = "#" + _id;
//    // console.log(_id);
    var ele = src;
//    // console.log(src);
//    // console.log(ele);
    ele = 'url(' + ele + ')';
    if (darkenbg)
        $(_id).css({ 'background-image': 'linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), ' + ele });
    else
        $(_id).css({ 'background-image': ele });
    // , 'filter': 'blur(5px)'
}


function loading(t = 2000) {
    setTimeout(function() {
        $('#myOverlay').show();
        $('#loadingGIF').show();
    }, t);
}

// $('a').click(function(){
//     loading(0);
// });

function ClickToGoTo(link, ele) {
    loading()
    $(ele).addClass('tada');
    $(ele).addClass('animated');
    $('body').addClass('stop-scrolling')
    window.open(link, '_self');
}

function vote(img_id, downvote = false) {
    if (downvote) {

        var url_ = '/post/downvote';

        if ($('.fa-arrow-up').hasClass('activeUVote')) {
            $('.fa-arrow-up').removeClass('activeUVote');
        }
        $('.fa-arrow-down').toggleClass('activeDVote');
        $('.fa-arrow-down').toggleClass('tada');
        $('.fa-arrow-down').toggleClass('animated');
    } else {

        var url_ = '/post/upvote';

        if ($('.fa-arrow-down').hasClass('activeDVote')) {
            $('.fa-arrow-down').removeClass('activeDVote');
        }
        $('.fa-arrow-up').toggleClass('activeUVote');
        $('.fa-arrow-up').toggleClass('tada');
        $('.fa-arrow-up').toggleClass('animated');
    }
    $.ajax({
        url: url_,
        method: 'POST',
        data: { 'img_id': img_id },
        success: function(data) {
//            console.log(data);
            window.location.reload();
        }
    })
}

function Edit(param) {
//    console.log(param);
    if (param.ele){
        ele = param.ele;
    }

    if (window.active){
        Discard(ele);
        window.active = false;
        return;
    }
    else{
        window.active = true;
    }

    if (param.isImg){
        isImg = true;
        var tag = 'textarea'
    }
    else{
        isImg = false;
        var tag = 'input'
    }

    var form_edit = `
    <div class="form-group" id='form-in'>
        <${tag} class="form-control" type = "${param.type|| 'text'}" id="form-in-main" name="description" placeholder="${param.placeholder || 'Write Image Description'}">
        </${tag}>
        <div class="d-flex justify-content-end mt-1">
            <a class="btn btn-outline-dark" 
            href="javascript:Discard('${ele}')" 
            style='font-size: 0.8em!important;'>
            Discard Changes
            </a>
            <a class="btn btn-dark ml-1" 
            href='javascript:Save({data_ : "${imgID || username}",
ele: "${ele}", isImg : ${isImg}, fieldType: "${param.fieldType || null}"})'
             style='font-size: 0.8em!important;'>Save Changes</a>
        </div>
    </div>`;
//    console.log(form_edit);
    if ($(ele).hasClass('d-none')){
        Discard(ele);
        return;
    }
    var element_value = $(ele).text();
    $(form_edit).insertAfter(ele);
//    // console.log('worked!');
    $('#form-in-main').val(element_value);
    $(ele).toggleClass('d-none');
}

function Save(param) {
//    // console.log('param : \n');
//    // console.log(param);
    if (param.data_) {
        var data_ = param.data_;
    } else {
//        console.log('data not provided for saving data');
    }

    if (param.ele) {
        var ele = param.ele;
    } else {
//        console.log('element not provided for fetching the data');
    }

    var content = $('#form-in-main').val();
//    console.log(content);

//    // console.log('isImg: '+ isImg);
    if (param.isImg) {
//        console.log('request to image update');
        var url_ = '/post/updDisc';
        var obj = { 'desc': content, 'img_id': data_ };
    }
    else{
//        console.log('request to api');
        var url_ = '/api';
        var obj = {
            'username': data_,
            'fieldType': param.fieldType,
            'data': content
        }
    }

//    console.log(obj);
    $.ajax({
        url: url_,
        type: 'PUT',
        data: JSON.stringify(obj),
        contentType: 'application/json',
        dataType: 'json',
        success: function(data) {

            if (data['success']) {
                if (param.isImg){
                    document.querySelector(ele).textContent = $('#form-in-main').val();
                    Discard(ele);
//                    console.log(data);
                }
                else{
                    window.location.reload();    
                }
            } else {
                window.location.reload();
            }

            // window.location.reload();
        }
    })
}

function Discard(ele) {
    $('#form-in').remove();
    $(ele).removeClass('d-none');
    window.active = false;
}

function loadImages(param) {
    if (param.skip != undefined && skip != 0)
        skip = param.skip;
    else
        skip = 0;

    if (param.cat != undefined)
        var cat = param.cat;
    else
        var cat = '';

    if (param.username != undefined)
        var username = param.username;
    else
        var username = '';

    if (param.url_ != undefined)
        var url_ = param.url_;
    else
        var url_ = '/images';

    obj = {
        'skip': skip,
        'category': cat,
        'username': username
    }
//    console.log(obj);
    $('#loadingImgs').toggleClass('d-none');
    $.ajax({
        url: url_,
        type: 'POST',
        data: JSON.stringify(obj),
        contentType: 'application/json',
        dataType: 'json',
        success: function(data) {
            if (data['images'].length == 0) {
                window.finished = true;
                $('#fin').removeClass('d-none');
                $('#loadingImgs').remove();
//                console.log('finished!');
                return null;
            } else if (window.skip == data['endCursor']) {
//                console.log('wtf!');
                return null;
            }
            loading_ = true;
//            console.log(data);
            render_images(data['images']);
            loading_ = false;
            window.skip = data['endCursor'];
        }
    });
}
function render_images(data, i = 0) {
//    console.log(data);
//    // console.log(img["img_id"],img["image"],img["description"])
    if (data[i] != undefined && data[i]['isProfile'] == false) {
        var template = `
        <a href='/post/${data[i]['img_id']}'>
            <div class="item animated bounceInRight">
                <img src="/images/display/${data[i]['img_id']}.jpg" alt="" class="image" style="width:100%;" onerror="$(this).remove()">
                <div class="middle">
                    <div class="mt-3 py-0" style="font-size: 1.2em; color: white; text-shadow: 1px 2px 8px black;"><p class='font-weight-thin mb-0'>Taken By</p>
                        <div class="text-center"><img src="${data[i]['hasProfilePicture'] ? `data:image/jpg;base64,${data[i]['profilePicture']}` : `${data[i]['profilePicture']}`}" class='my-0 mini-profile-picture' alt="" style="width: 30%">
                        <p class='font-weight-bold'>${data[i]['name']}</p>
                        </div>
                    </div>
                </div>
            </div>
        </a>`;
    } else if (data[i] != undefined && data[i]['isProfile'] == true) {
        var template = `
        <a href="/post/${data[i]['img_id']}">
            <div class="item animated bounceInRight">
                <img src="/images/display/${data[i]['img_id']}.jpg" alt="" class="image" style="width:100%" onerror="$(this).remove()">
                <div class="middle">
                    <div class="text">${data[i]['description'] || moment(data[i]['created_at']).format("dddd, MMMM Do YYYY, h:mma")}</div>
                </div>
            </div>
        </a>`;
    }
    // $('.masonry').append();
    setTimeout(function() {
        if (data.length + 1 > i) {
            $('#loadingImgs').toggleClass('d-none');
            $('.masonry').append(template);
            loading_ = true;
            render_images(data, ++i);
            loading_ = false;
        }
    }, 200);
}
// passwordField.addEventListener( 'keydown', function( event ) {
//   var caps = event.getModifierState && event.getModifierState( 'CapsLock' );
//  // console.log( caps ); // true when you press the keyboard CapsLock key
// });
var nav1 = false;
var nav2 = false;

$('[data-target="#navbarToggle"]').click(function() {
    if (!nav2 || !($('.scrollmenu').hasClass('d-none'))){
        nav1 = !(nav1);
        $('.scrollmenu').toggleClass('d-flex');
        $('.scrollmenu').toggleClass('d-none');
    }
})

$('[data-target="#search_"]').click(function() {
    if (!nav1 || !($('.scrollmenu').hasClass('d-none'))){
        nav2 = !(nav2);
        $('.scrollmenu').toggleClass('d-flex');
        $('.scrollmenu').toggleClass('d-none');
    }
})