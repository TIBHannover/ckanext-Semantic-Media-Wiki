$(document).ready(function(){
    $.ajax({
        url: $('#get_link_url').val(),
        cache:false,   
        dataType: 'json',      
        type: "GET",
        success: function(result){
            if(result == '0'){
                $('#machine_link_box').hide();
            }
            else{
                $.each(result, function(key,value){
                    if (value.exists) {
                        $('#equipment_list').append(
                            $('<a>', {href: value.url, target: '_blank', text: key}),
                            '<br>'
                        );
                    } else {
                        $('#equipment_list').append($('<span>', {text: key}), '<br>');
                    }
                });

            }            
        }
    });



});
