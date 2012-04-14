<?php
	session_start();
	
	if (isset($_REQUEST['j'])){
		include_once('protocolhandler.php');
		try{
			$protocolHandler = new ProtocolHandler($_REQUEST['j']);
			$protocolHandler->execute();
		} catch (Exception $e) {
			echo "{'error':".$e->getMessage()."}";
		}
		echo $protocolHandler->getResult();
	}else{
		include_once('repository.php');
		$repository = Repository::getInstance();
?>
<!DOCTYPE HTML>
<html>
	<head>
		<title>Scoville Repository</title>
		<meta name="description" content="Scoville Repository">
		<meta name="author" content="Scoville">
		<style type="text/css">
			body {
			  padding: 0px;
			  margin: 0px;
			  background-color: #e1e1e1;
				font-family:Arial,Helvetica,Verdana;
				color: #555;
				font-size:12px;
			}
			
			a {
				color:#666;
			}
			
			a:hover{
				color:#777;
			}
			
			div#head {
			  height: 100px;
			  background:-moz-linear-gradient(top, #b7b7b7, #e1e1e1);
			  background:-webkit-gradient(linear, left top, left bottom, from(#b7b7b7), to(#e1e1e1)); 
			}
			
			div#left {
			  position: absolute;
			  top: 100px;
			  left: 0px;
			  width: 160px;
			  bottom: 0px;
				margin-left:3px;
			}
			
			div#content {
			  position: absolute;
			  width: 600px;
			  top: 100px;
			  left: 162px;
			  right: 0px;
			  bottom: 0px;
			  border-left: 1px solid silver;
				padding-left:20px;
			}
			
			div#login {
			  width: 250px;
			  margin-top: 100px;
			  margin-left: 100px;
			  text-align: right;
			}
			
			div#login input[type=submit] {
			  margin-right: 50px;
			}
			
			div.info{
				border: 1px dashed silver;
			}
			
			p.info{
				 text-align:justify;
				 line-height: 200%;
			 }
			
			p{
				 text-align:justify;
				 line-height: 200%;
			}
		</style>
	</head>
	<body>
		<div id="head">
	    	<a id="begin"><img src="repo.png"></a>
	    </div>
	    <div id="left">
		    <p>Scoville Repository<br></p>		
	    </div>
	    <div id="content">
	    	This is a Scoville repository. It supplies Modules and Templates for Scoville Instances.
	    	
	    	The data provided is signed via RSA to ensure that there is no manipulated data coming onto
	    	your server.
	    	
	    	This repository's RSA public key is:
	    	<div class="info">
	    		<p><?php echo $repository->getPublicKeyForPage(); ?></p>
	    	</div>
	    	
	    	Register this Repository with your Scoville Admintool if you trust the maintainer.
	    </div>
	</body>
	
</html>		
<?php
	}
?>