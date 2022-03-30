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
                    let anchor = '<a href="';
                    anchor += value;
                    anchor += ('" target="_blank">' + key + '</a><br>');
                    $('#equipment_list').append(anchor);
                });

            }            
        }
    });



});

