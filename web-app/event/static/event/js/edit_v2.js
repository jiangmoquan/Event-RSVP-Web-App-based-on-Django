// 关于未保存时的刷新：应该像博客园那样，刷新的时候提示“是否要保存”，如果选择不保存，一切改动无效

// 每次打开网页，生成一个空的、隐藏的questionItem，放在<ol>标签的开头，做克隆的模板
var $form = $("form");

$(function () {
    $(".questionItem:first").clone().attr({"qid": null, "id": 'modelItem'}).addClass('hidden').prependTo($("form ol"));

    // 清空input框
    $("input[name=title]:first").val('');
    // 重置option标签的selected属性
    var $new_options = $("select[name=type]:first").children();
    $new_options.attr('selected', false);
    $new_options.first().attr('selected', true);

    var $model_ul = $(".questionItem ul:first");
    if ($model_ul.children().length) {
        // 如果克隆的model_questionItem是单选类型，清空选项
        $model_ul.html('');
    }
    if ($model_ul.next().children().length) {
        // 如果克隆的model_questionItem是单选类型，清空选项
        $model_ul.next().html('');
    }
});


// 添加问题
$("#addQue").click(function () {
    $("#modelItem").clone().attr("id", null).removeClass('hidden').appendTo($("form ol"));
});


// 删除问题
$form.on('click', '.removeQue', function () {
    $(this).parent().parent().parent().remove();
});


// select框的change事件委派
$form.on('change', 'select', function () {
    if ($(this).children(':selected').val() === '2') {
        // 如果用户选择的是单选类型，显示“添加选项”按钮，并添加一组选项
        $(this).parent().next().removeClass('hidden');
        $(this).parent().parent().next().html('');
        var s = '<div class="form-group">\n' +
            '<label class="control-label col-md-1">● Content</label>\n' +
            '<div class="col-md-2">\n' +
            '    <input type="text" name="content" class="form-control" maxlength="16">\n' +
            '</div>\n' +
            '<div class="removeOpt"><span class="glyphicon glyphicon-remove"></span></div>\n' +
            '</div>';
        $(this).parent().parent().next().append(s);
    }
    else {

        // 如果用户选择的是其他类型，隐藏“添加选项”按钮，并清空选项
        $(this).parent().next().addClass('hidden');
        $(this).parent().parent().next().html('');
        $(this).parent().parent().next().next().html('');
        if ($(this).children(':selected').val() === '1') {
            var s = '<div class="form-group">\n' +
                '<label class="col-md-1 col-md-offset-1 control-label">Max Add Value</label>\n' +
                '<div class="col-md-7">\n' +
                '    <input type="number" name="max_value" class="form-control" maxlength="16">\n' +
                '</div>\n' +
                '</div>';
            $(this).parent().parent().next().append(s);
        }
    }
});


// 添加选项
$form.on('click', '.addOpt', function () {
    var s = '<div class="form-group">\n' +
        '<label class="control-label col-md-1">● Content</label>\n' +
        '<div class="col-md-2">\n' +
        '    <input type="text" name="content" class="form-control" maxlength="16">\n' +
        '</div>\n' +
        '<div class="removeOpt"><span class="glyphicon glyphicon-remove"></span></div>\n' +
        '</div>';
    $(this).parent().parent().next().append(s);
});


// 删除选项
$form.on('click', '.removeOpt', function () {
    $(this).parent().remove();
});


// 点击保存，提交ajax请求#############################
$("#save").click(function () {
    var data_list = [];
    $(".questionItem:gt(0)").each(function () {
        var temp_dict = {
            "qid": Number($(this).attr('qid')),
            "title": $(this).find('input[name=title]').val(),
            "type": Number($(this).find('select[name=type]').val()),
            "options": [],
            "max_value": Number($(this).find('input[name=max_value]').val()),
            "vendor_view": $(this).find('input[name=vendor_view]').is(':checked'),
        };
        if (temp_dict['type'] === 2) {
            $(this).find('ul>.form-group').each(function () {
                temp_dict['options'].push({
                    "oid": Number($(this).attr('oid')),
                    "content": $(this).find('input[name=content]').val(),
                })
            })
        }
        data_list.push(temp_dict);
    });
    // console.log(data_list);

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
});