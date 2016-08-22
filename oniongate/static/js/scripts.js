// (function ($) {

// })(jQuery);

$(function() {

  $.fn.serializeFormJSON = function () {

      var o = {};
      var a = this.serializeArray();
      $.each(a, function () {
          if (o[this.name]) {
              if (!o[this.name].push) {
                  o[this.name] = [o[this.name]];
              }
              o[this.name].push(this.value || '');
          } else {
              o[this.name] = this.value || '';
          }
      });
      return o;
  };

  var remove_form_errors = function(form){
    $(".help-block", form).hide();
    $(".has-error", form).removeClass("has-error");
  }

  $("#subdomain-signup-form").on("submit", function(event) {
    var form = this;
    $(".form-success-alert", form).hide()

    console.log($(this).serializeFormJSON());

    $.ajax({
      type: "POST",
      url: $API_ROOT + "/domains",
      dataType: 'json',
      data: JSON.stringify($(this).serializeFormJSON()),
      contentType: "application/json",
      success: function (data, text) {
          remove_form_errors(form);
          $(".form-success-alert", form).show()
      },
      error: function (request, status, error) {
          remove_form_errors(form);

          // Parse the API result and add all error messages to the fields
          var response_json = $.parseJSON(request.responseText);
          $.each(response_json['message'], function (field_name, error_message) {
            $("." + field_name + "_help", form).show().html(error_message);
            $("." + field_name + "_group", form).addClass('has-error');
          });
      }
    });
    event.preventDefault();
  });

});
