$(document).ready(function(){
    let anchors = $('.machine-link');
    for(let i=0; i<anchors.length; i++){        
        get_resource_link(anchors[i] ,$(anchors[i]).siblings('.base_url').val());
    }

});

function get_resource_link(target, url){    
    $.ajax({
        url: url,
        cache:false,   
        dataType: 'json',     
        type: "GET",
        success: function(result){            
            if(result == '0'){                
                $(target).find('.machine-name-tag').css('visibility', 'hidden');
            }
            else{                
                $(target).attr('href', result[0]);
                $(target).find('.machine-name-tag').text(result[1]);
                $(target).show();
                
            }            
        }
    });
}