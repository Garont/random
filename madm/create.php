<?
session_start();


if ($_SERVER['REQUEST_METHOD'] === 'POST') {

$_SESSION["logpass"] = $_POST["value"];

}else{

$login = escapeshellarg($_SESSION["logpass"][0]);
$password = escapeshellarg($_SESSION["logpass"][1]);
$allconfig = parse_ini_file(getcwd().'/config.ini');
$domain = $allconfig["hosts"];
$saslpasswd = $allconfig["saslpasswd"];

$mailtest = shell_exec("sasldblistusers2 | grep ^".$login."@".$domain);

if (isset($mailtest)) { //testing sasl account for existance
        $mailtest = explode(': userPassword', $mailtest); //deleting userPassword
        $mailtest = array_slice($mailtest, 0, -1); //deleting empty string at the end

        foreach ($mailtest as $mailbox) {
                print $mailbox." already exists!<br>";
        }
        $_SESSION["logpass"] ="";

}else{ //creating sasl acc
        try {
        shell_exec("echo ".$password." | saslpasswd2 -p -c ".$login." -p");
        shell_exec("expect -c 'spawn cyradm -user cyrus localhost;expect Password:;send \"".$saslpasswd."\n\";expect localhost>;send \"cm user/".$login."\n\";expect localhost>;send \"sam user/".$login." cyrus c\n\";expect localhost>;send \"exit\n\";'");
        print "Email created";
        $_SESSION["logpass"] ="";
        } catch (Exception $e) {
                print $e;
        }
        }//end else
}//end POST else
?>
