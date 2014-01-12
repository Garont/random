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
p{
font-family : monospace ! important;
}
</style>

</head>
    <body>
        <p><pre><?=($filecontents);?></pre><p>
    </body>
</html>
