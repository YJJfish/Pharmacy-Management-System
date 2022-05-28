(function(){
    function readURL(input) {

        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('.avatar-bg').css({
                    'background':'url('+e.target.result+')',
                    'background-size':'cover',
                    'background-position': '50% 50%'
                });
            };

            reader.readAsDataURL(input.files[0]);
        }
    }
    
    function toggleAlert(clasz, display){
        $(".alert")
            .removeClass("display")
            .removeClass("alert-info")
            .removeClass("alert-success")
            .removeClass("alert-danger")
            .addClass(clasz);
        if(display){
            $(".alert").addClass("display")
        }
        if(clasz === "alert-success"){
            $(".alert > span").text('Profile saved');
        }else if(clasz === "alert-danger"){
            $(".alert > span").text('Profile reset');
        }
    }

    $("input.form-control[name=avatar-file]").change(function(){
        readURL(this);
    });
    
    $('#profile').delegate('form', 'submit', function (e) {
        var inst = this;
        var formData = new FormData($(this)[0]);

        $(inst).find("button[type = submit]").addClass("loading").prop("disabled", true);
        toggleAlert("alert-success", true);
        
        setTimeout(function(){
            $(inst).find("button[type = submit]").removeClass("loading").prop("disabled", false);
            toggleAlert("alert-success");
        },1000);
        
        return false;
    });
    
    $('#profile').delegate('form', 'reset', function (e) {
        var inst = this;
        var formData = new FormData($(this)[0]);

        $(inst).find("button[type = reset]").addClass("loading").prop("disabled", true);
        toggleAlert("alert-danger",true);
        
        setTimeout(function(){
            $(inst).find("button[type = reset]").removeClass("loading").prop("disabled", false);
            toggleAlert("alert-danger");
        },1000);
        
        return false;
    });
})()