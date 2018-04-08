
// 点击保存，提交ajax请求#############################
$("#save").click(function () {
    var data_list = [];
    var flag = 0;
    $(".questionItem").each(function () {
        var temp_dict = {
            "qid": Number($(this).attr('qid')),
            "type": Number($(this).attr('q_type')),
            "finalized": $(this).find('input[name=finalized]').is(':checked'),
        };


        data_list.push(temp_dict);
    });
    // console.log(data_list);

    if (flag == 0){
        $.post({
        url: location.pathname,
        headers: {"X-CSRFToken": $.cookie('csrftoken')},
        data: JSON.stringify(data_list),
        contentType: 'application/json',
        success: function (res_dict) {
            if (res_dict['status']) {
                location.href = '/event';
            }
            else {
                alert(res_dict['error_msg']);
            }
        }
    })
    }

});