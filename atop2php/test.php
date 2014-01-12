<?
// ./atop.bash ; disown

$page = $_SERVER['PHP_SELF'];
$sec = "10";

$filecontents = file_get_contents("/var/www/site/atop.txt");
?>
<html>
    <head>
    <meta http-equiv="refresh" content="<?php echo $sec?>;URL='<?php echo $page?>'">

<style type="text/css">
body{
    background-color: #000000;
   }
p{
font-family : monospace ! important;
color:rgb(255,255,255);
}
</style>

</head>
    <body>
        <pre><p><?=($filecontents);?></p></pre>

    </body>
</html>
