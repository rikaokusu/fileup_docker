$(function(){
    // jquery validateを使ったフロントエンドバリデーション
    $.extend($.validator.messages, {
        email: '正しいメールアドレスを入力して下さい。',
        equalTo: 'もう一度同じ値を入力して下さい。',
        minlength: '{0}文字以上入力して下さい。',
        required: '入力して下さい。',
        digits: '整数を入力してください',
    });
    
    // 新規登録用バリデーション
    $('#my_form').validate({
        rules: {
            'user-email': {
                required: true,
                // email: true,
                // CustomValidateEmail: true,
            },
            "company-pic_company_name": {
                // CustomValidateUserCompanyName: true,
                required: true,
                // 個人事業主にチェックが入っている場合は法人格のチェックをしない
                // required:{
                // CustomValidateUserCompanyName: {
                // depends: function(element) {
                // return !($('input:checked').val() == 'on');
                // }
                // },
            },
            // "user-password1":{
            //     required:true,
            //     //CustomValidateUserPassword: true,
            // },
            // "user-password2":{
            //     required:true,
            //     //CustomValidateUserPassword: true,
            // },
        },
        messages: {
            "user-email": {
                required: 'メールアドレスは必須です。',
                // email: '正しいメールアドレスを入力してください。',
                // CustomValidateEmail: 'このメールアドレスは使用できません。',
            },
            "company-pic_company_name": {
                required: '会社名は必須です。',
                CustomValidateUserCompanyName: '法人格を入力してください',
            },
            // "user-password1":{
            //     required:"パスワードは必須です。",
            //     CustomValidateUserPassword: 'パスワードを入力してください。',
            // },
            // "user-password2":{
            //     required:"確認用パスワードは必須です。",
            //     CustomValidateUserPassword: '確認用パスワードを入力してください。',
            // },
        },
        errorPlacement: function(error, element) {
          // console.log(error)
          // console.log(element)
          // error.insertAfter($("#" + element.attr("name") + "_err") )
          error.insertAfter($("#" + element.attr("name")))
        },
    });

    // メールアドレス用カスタムバリデーション
    // jQuery.validator.addMethod(
    //   "CustomValidateEmail",
    //   function(val,elem){
    //     // console.log(val);
    //     // console.log(elem);
    //     reg = new RegExp(/([\w]+@[\w]+?\.?(ocn\.ne\.jp|so-net\.ne\.jp|biglobe\.ne\.jp|nifty\.com|asahi-net\.or\.jp|wakwak\.com|plala\.or\.jp|yahoo\.co\.jp|hotmail\.com|hotmail\.co\.jp|ybb\.ne\.jp))|([\w]+@(ocn\.ne\.jp|so-net\.ne\.jp|biglobe\.ne\.jp|nifty\.com|asahi-net\.or\.jp|wakwak\.com|plala\.or\.jp|yahoo\.co\.jp|hotmail\.com|hotmail\.co\.jp|ybb\.ne\.jp))/);
    //     // console.log(reg);
    //     // console.log('テスト　バル')
    //     // console.log(reg.test(val));
    //     // console.log('オプション　エルム')
    //     // console.log(this.optional(elem));
    //     // console.log('メール　かつ')
    //     // console.log(this.optional(elem) || !reg.test(val));
    //     // console.log('メール　＆＆')
    //     // console.log(this.optional(elem) && reg.test(val));
    //     return this.optional(elem) || !reg.test(val);
    //   },
    //   ""
    // );

    // 会社名用カスタムバリデーション
    jQuery.validator.addMethod(
        "CustomValidateUserCompanyName",
        function(val,elem){
          // console.log(val);
          // console.log(elem);
          reg = new RegExp("(^(株式会社|合同会社|合名会社|合資会社|一般社団法人|一般財団法人|特定非営利活動法人|有限責任事業組合).*)|(^.*(株式会社|合同会社|合名会社|合資会社|一般社団法人|一般財団法人|特定非営利活動法人|有限責任事業組合))");
          // console.log(reg);
          // console.log(reg.test(val));
          // console.log(this.optional(elem));
          // console.log(this.optional(elem) || reg.test(val));
          return this.optional(elem) || reg.test(val);
        },
        ""
      );

    // //パスワードリセットのみ用バリデーション
    // $('#my_form2').validate({
    //     rules: {
    //         "user-password1":{
    //             required:true,
    //             CustomValidateUserPassword: true,
    //         },
    //         "user-password2":{
    //             required:true,
    //             CustomValidateUserPassword: true,
    //         },
    //     },
    //     messages: {
    //         "user-password1":{
    //             required:"パスワードは必須です。",
    //             CustomValidateUserPassword: 'パスワードを入力してください。',
    //         },
    //         "user-password2":{
    //             required:"確認用パスワードは必須です。",
    //             CustomValidateUserPassword: '確認用パスワードを入力してください。',
    //         },
    //     },
    //     errorPlacement: function(error, element) {
    //       error.insertAfter($("#" + element.attr("name")))
    //     },
    // });

    // パスワードの強化チェック用バリデーション
    var $form = $(".password_form");

      var label2 = ""
    
    // submitイベントをキャンセル
    function formCancelSubmit(){
      $form.off("submit").on("submit", function(e){
        alert("パスワードの強度が基準値に達していません。\n数字や記号を追加し文字数を増やしてください。");
        e.preventDefault();
      });
    }

    $("#user-password1").pwdMeasure({
      minScore: 50,
      minlength: 8,
      indicator: "#pm-indicator",
      confirm: "#user-password2",
        //   indicatorTemplate: "<%= label %>",
      indicatorTemplate: "パスワード判定: <%= label %>",
      events: "keyup",
      labels: [
      {score:45, label:"NG", className:"weak"},
      {score:100, label:"OK", className:"strong"},
      {score:"notMatch", label:"不一致", className:"not-match"},
      {score:"empty", label:"未入力", className:"empty"}
      ],
        
        // PWの強度が入ったpercentageをformCancelSubmitに渡す
        //   formCancelSubmit(percentage, className);
        //   $("submit").prop("disabled", false)
        //   },
      //コールバック(有効)
      onValid: function(percentage, label, className){
        $form.off("submit");
        // var form = $('form').attr('id')
        
        // var valid = $(form).validate().checkForm();
        // console.log(valid)
        //   console.log("valid")
        //   console.log(label)
        //   label2 = label
        //$form.off("submit");
        $('#send').prop("disabled", false)
        console.log("いけてる",className)
        // if(valid){
        //     $('#send').prop("disabled", false)
        // } else {
        //     $('#send').prop("disabled", true)
      },
  
      //コールバック(無効)
      onInvalid: function(percentage, label, className){
//           console.log("invalid")
//           //formCancelSubmit(className);
//           console.log("invalid", className)
// //          $('#send').prop("disabled", true)
//             label2 = label

//         valid = false
//         console.log(valid)
//         if(valid){
//             console.log("a")
//             $('#send').prop("disabled", false)
//         } else {
//             console.log()
//             $('#send').prop("disabled", true)
//         }
        console.log("失敗～～～～",className)
        formCancelSubmit();
        
        },
      
      onNotMatch: function(label,className){
        // label2 = label
        // valid = false
        // console.log("onNotMatch")
        $('#send').prop("disabled", true)
        console.log("あってない",className)
        },
    });
    
    // $("#user-password1 , #user-password2").on('input', function () {
    //     console.log("label",label2)
    //     if(label2=="不一致") {
    //         console.log("vvv")
    //         var result = $('#send').prop("disabled");
    //         console.log("result" , result)
    //         if (result){
    //             console.log("hhhh")
    //             setTimeout(function(){
    //                 $('#send').prop("disabled", true);
    //             },10);

    //         }

        // }

    // });    

});
