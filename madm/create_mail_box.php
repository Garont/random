<body>

  <div class="navbar navbar-inverse navbar-fixed-top">
    </div>

    <div class="container-fluid">
      <div class="row-fluid">
        <div class="span3">
          <div class="well sidebar-nav">

<?

$sasllist = shell_exec("sasldblistusers2");
$saslarray = explode(': userPassword', $sasllist);

$allconfig = parse_ini_file(getcwd().'/config.ini');
$domain = $allconfig["hosts"];

?>

<div class="spoiler">
    <!-- <input type="button" onclick="showSpoiler(this);" value="Show all emails" /> -->
    <button class="btn" onclick="showSpoiler(this);return false;"><i class="icon-list"></i> Show all emails</button>
    <div class="inner" style="display:none;">


<?
foreach ($saslarray as $value) {
    echo "  ".$value."<br>";
}
?>

    </div>
</div>

          </div><!--/.well -->
        </div><!--/span-->
        <div class="span5">
          <div class="hero-unit">
     <form method="post" action="" target="" name="postform" class="postform" id="postform">
            <h3><legend>Create Email:</legend></h3>
            <div class="input-append">
            <input type="text" id="login" class="input-small" placeholder="Login"></input><span class="add-on">@<?=$domain?></span>
            </div>
            <br>
            <div class="input-append">
            <input type="text" id="password" placeholder="Password"></input> <button id="signin_button" class="btn btn-info" onclick="randompass();return false;" ><i class="icon-white icon-lock"></i> Gimme random password plz</button>
            </div>
            <br>
            <button id="signin_button" class="btn btn-success" onclick="postshit();return false;"><i class="icon-white icon-envelope"></i> Create email </button>
           <!--  <input type="button" value="Work, God damn you!" onclick="postshit()"></input>  -->
     </form>

      <div id="content"></div>

          </div>

         </div>
</body>
                                                                                                                                                        66,7        Внизу
