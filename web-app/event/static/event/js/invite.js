
$("#submit_btn").click(function () {
    var email=$("#email-input");
    var options=$("#select-role option:selected");



    var $help1 = $("#help-email").html('');
    var $help2 = $("#help-role").html('');

    if (!$title.val()) {
        $help1.html('Input Email');
    }
    else if (!$date.val()) {
        $help2.html('Choose Role');
    }
    else {

        $.post({
            url: './',
            headers: {"X-CSRFToken": $.cookie('csrftoken')},
            data: JSON.stringify({"email": email.val(), "role": options.text()}),
            contentType: 'application/json',
            success: function (res_dict) {
                if (res_dict['status']) {
                    var userid = res_dict['user'];
                    var role = res_dict['role'];

                    var s = '<tr id="user_' + userid.id + '">\n' +
                        '        <td>' + email.val() + '</td>\n' +
                        '        <td>' + userid.username + '</td>\n' +
                        '        <td>' + $options.text() + '</td>\n' +
                        '        <td><a href="javascript:void (0)" class="delete">Delete</a></td>\n' +
                        '    </tr>';
                    $("tbody").append(s);

                }
                else {
                    var error_msg = res_dict['error_msg'];
                    //UNIQUE constraint failed: ...
                    if (new RegExp("UNIQUE constraint failed").test(error_msg)) {
                        alert('该问卷已存在，请勿重复添加！')
                    }
                }
            }
        });

    }
});