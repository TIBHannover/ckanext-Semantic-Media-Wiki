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
                    let anchor = '<a href="';
                    anchor += value;
                    anchor += ('" target="_blank">' + key + '</a><br>');
                    $('#sample_list').append(anchor);
                });

            }            
        }
    });
});

