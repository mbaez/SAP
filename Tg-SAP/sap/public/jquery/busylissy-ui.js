$(document).ready(function(){

    $('a.action-delete').click(function(event) {
        event.preventDefault();
        url = $(this).attr('href');
        jConfirm('really?', 'Are you sure?', function(r) {
            if(r == true){
                location.href = url;
            }
        });
    });

    $('#js-addtask').each(function(){
        $('.insert-tag-link').click(function(event){
            event.preventDefault();
            var tag = $(this).text();
            var comma = ", ";

            $(this).parent().fadeOut("slow");
            var tag_string = $('#id_tags').val();
            if(tag_string.lastIndexOf(",") != (tag_string.length - 1) && tag_string.lastIndexOf(",") != (tag_string.length - 2) || ((tag_string.length > 0) && tag_string.length < 2)){
                $('#id_tags').val($('#id_tags').val() + comma);
            }

            $("#id_tags").val($("#id_tags").val() + tag + comma);

        });
    });


    $('#js-addtask .insert-tag-link').each(function(){
        var tag = $(this).text();

        if($('#id_tags').val().indexOf(tag) != -1){
            $(this).parent().fadeOut("slow");
        }
    });

    // Datepicker
    $('#id_due_date').datepicker({ dateFormat: 'yy-mm-dd' });
    $('#id_birth_date').datepicker({ dateFormat: 'yy-mm-dd' });
    $('#id_day').datepicker({ dateFormat: 'yy-mm-dd' });

    // Add members
    $('#member a').each(function(){
        $(this).click(function(event){
            event.preventDefault();
            var comma = ", ";
            user_string = $('#id_usernames').val();
            if(user_string.lastIndexOf(",") != (user_string.length - 1) && user_string.lastIndexOf(",") != (user_string.length - 2) || ((user_string.length > 0) && user_string.length < 2)){
                $('#id_usernames').val($('#id_usernames').val() + comma);
            }
            $("#id_usernames").val($("#id_usernames").val() + $(this).find('img').attr("alt") + comma);
            $(this).parent().fadeOut("slow");
        });
    });

    $("#id_usernames").keyup(function(){
        $('#member a').each(function(){
            var member = $(this).find('img').attr("alt");

            if($('#id_usernames').val().indexOf(member) == -1){
                $(this).parent().fadeIn("slow");
            } else {
                $(this).parent().fadeOut("slow");
            }
        });
    });

    $('#member a').each(function(){
        var member = $(this).find('img').attr("alt");

        if($('#id_usernames').val().indexOf(member) != -1){
            $(this).parent().hide();
        }
    });


    // Colorize projects
    var color_arr = new Array("#e6abb8", "#e5a65c", "#95c790", "#a5b4e4", "#9fe6db", "#bababa","#cd9de4", "#d1a891", "#6ec0d0", "#e5988c", "#d0cf82", "#97e5b1", "#c896a2", "#cb9454", "#82ae7e", "#8893be", "#85c3ba", "#a4a4a4", "#b087c5", "#b38f7d", "#bd7d75", "#b0b06e", "#83c79c");
    $('.project-calendar li a').each(function(item){
        var color = color_arr[item];

        $(this).next().css({'background-color': color });
        var project = $(this).attr("href");
        $('#agenda li').each(function(){
            var name = $(this).find('a').attr("name").split(" ");
            if(name[0] == project){
                $(this).css({'background-color': color });
            }
        });
    });
});

