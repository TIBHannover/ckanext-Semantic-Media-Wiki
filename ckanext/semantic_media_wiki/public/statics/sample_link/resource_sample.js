$(document).ready(function(){
    $.ajax({
        url: $('#get_sample_url').val(),
        cache:false,   
        dataType: 'json',      
        type: "GET",
        success: function(result){
            if(result == '0'){
                $('#sample_link_box').hide();
            }
            else{
                $.each(result, function(key,value){
                    if (value.exists) {
                        $('#sample_list').append(
                            $('<a>', {href: value.url, target: '_blank', text: key}),
                            '<br>'
                        );
                    } else {
                        $('#sample_list').append($('<span>', {text: key}), '<br>');
                    }
                });

            }            
        }
    });
});
