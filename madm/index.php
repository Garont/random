<?
session_start();
?>

<!DOCTYPE html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
 <title>Email Editor</title>

<link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.min.css" rel="stylesheet">
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>


    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
      .sidebar-nav {
        padding: 9px 0;
      }

      @media (max-width: 980px) {
        /* Enable use of floated navbar text */
        .navbar-text.pull-right {
          float: none;
          padding-left: 5px;
          padding-right: 5px;
        }
      }

      .spoiler
    {
    padding:5px;
    }

    </style>
 <script type="text/javascript">
        function showSpoiler(obj)
    {
    var inner = obj.parentNode.getElementsByTagName("div")[0];
    if (inner.style.display == "none")
        inner.style.display = "";
    else
        inner.style.display = "none";
    }
    </script>


 <script type="text/javascript">

function checkcreate(){

           $.ajax({
                    type: "GET",
                    url: "create.php",
                    cache: false,
                    success: function(html){
                        $("#content").html(html);
                    }
                });
         }

var arraybitch = [];

function postshit() {

  if(document.getElementById('login').value.length < 2 || document.getElementById('login').value.length > 15 || document.getElementById('password').value.length < 6 || document.getElementById('password').value.length > 15){
    alert("Login length must be from 2 to 15 symbols and password length must be from 6 to 15 symbols");
  }else{

   var Logogin = document.getElementById('login').value;
   arraybitch[0] = Logogin;
   var Paswaword = document.getElementById('password').value;
   arraybitch[1] = Paswaword;
   console.log(arraybitch);

   $.post('create.php', {value: arraybitch})

  var delay = 1000;
  setTimeout(checkcreate, delay);
}//end else
}

function randompass() {
document.getElementById('password').value = Math.random().toString(36).slice(-10);
}

</script>
</head>
<? require_once('create_mail_box.php') ?>
</html>
