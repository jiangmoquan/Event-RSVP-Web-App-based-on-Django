$("#add").click(function () {
    $("#id_event_name").val('');
    $("#id_event_time").val('');

});


$("#save").click(function () {
    var $title = $("#id_event_name");
    var $date = $("#id_event_time");
    console.log($title.val())

    var $help1 = $("#help-title").html('');
    var $help2 = $("#help-classroom").html('');

    if (!$title.val()) {
        $help1.html('Input a name!');
    }
    else if (!$date.val()) {
        $help2.html('Input a date!');
    }
    else {
        $("#add_naire").modal('hide');

        $.post({
            url: 'add/',
            headers: {"X-CSRFToken": $.cookie('csrftoken')},
            data: JSON.stringify({"title": $title.val(), "classroom_id": $date.val()}),
            contentType: 'application/json',
            success: function (res_dict) {
                if (res_dict['status']) {
                    var event_id = res_dict['event_id'];
                    var questionnaire_id = res_dict['questionnaire_id'];

                    var s = '<tr id="event_' + event_id + '">\n' +
                        '        <td>' + $title.val() + '</td>\n' +
                        '        <td>' + $date.val() + '</td>\n' +
                        '        <td><a href="/event/invite/' + event_id + '/">Edit Invitation</a></td>\n' +
                        '        <td><a href="/event/edit/' + questionnaire_id + '/">Edit Question</a></td>\n' +
                        '        <td><a href="/event/view-response/' + questionnaire_id + '/">View Response</a></td>\n' +
                        '        <td><a href="javascript:void (0)" class="delete">Delete Event</a></td>\n' +
                        '    </tr>';
                    $("tbody:first").append(s);

                }
                else {
                    var error_msg = res_dict['error_msg'];
                    //UNIQUE constraint failed: ...
                    if (new RegExp("UNIQUE constraint failed").test(error_msg)) {
                        alert('Do not repeat add!！')
                    }
                }
            }
        });

    }
});



$("tbody").on('click', '.delete', function () {
    if (confirm('确认删除？')) {
        var $remove_el = $(this).parent().parent();
        $.get({
            url: '/delete/',
            data: {
                'naire_id': $remove_el.attr('id').split('_')[1]
            },
            success: function (res_dict) {
                if (res_dict['status']) {
                    $remove_el.remove();
                }
                else {
                    alert(res_dict['error_msg']);
                }
            }
        })
    }
});

