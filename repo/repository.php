<?php
	include_once('database.php');
	#include_once('Crypt_RSA');
	
	
	abstract class Singleton {
		abstract public static function getInstance();
	
		abstract protected function init();
	}
	
	class Repository extends Singleton{
		private static $instance = null;
	
		public static function getInstance(){
			if (Repository::$instance==null){
				Repository::$instance = new Repository();
				Repository::$instance->init();
			}
			return Repository::$instance;
		}
		
		protected function init(){}
		
		private function rrmdir($dir) {
			if (is_dir($dir)) {
				$objects = scandir($dir);
				foreach ($objects as $object) {
					if ($object != "." && $object != "..") {
						if (filetype($dir."/".$object) == "dir") rrmdir($dir."/".$object); else unlink($dir."/".$object);
					}
				}
				reset($objects);
				rmdir($dir);
			}
		}
		
		private function establishConection(){
			$con = new repo_database();
			$con->set_all("zigapeda","10.8.0.58","scvrepo.gdb","test");
			$con->connect();
			return $con;
		}
		
		public function getAllModules(){
			$con = $this->establishConection();
			$resultset = $con->query("select mod_displayname, mod_md5, mod_name, mod_versionmajor, mod_versionminor, mod_versionrev
				from modules join (select mod_name vername 
				,max(mod_versionmajor*10000000 
				+mod_versionminor*100000 
				+mod_versionrev) ver 
				from modules 
				group by mod_name) 
				on vername = mod_name 
				and ver = mod_versionmajor*10000000 
				+mod_versionminor*100000 
				+mod_versionrev");
			$modules = array();
			while($result = $con->fetchArray($resultset)){
				$modules[] = array('name'=>$result["MOD_NAME"],
									 'hrname'=>$result["MOD_DISPLAYNAME"],
									 'version_major'=>$result["MOD_VERSIONMAJOR"],
									 'version_minor'=>$result["MOD_VERSIONMINOR"],
									 'revision'=>$result["MOD_VERSIONREV"],
									 'md5'=>$result["MOD_MD5"]);		
			}
			return json_encode(array("r"=>$modules));
		}
		
		public function getVersionsOfModule($module){
			$con = $this->establishConection();
			$resultset = $con->query("select mod_name, mod_displayname, mod_md5, mod_id, mod_versionmajor, mod_versionminor, mod_versionrev from modules 
										where mod_name = ? ;",array($module->name));
			$modules = array();
			while($result = $con->fetchArray($resultset)){
				$modules[] = array('name'=>$result["MOD_NAME"],
									 'hrname'=>$result["MOD_DISPLAYNAME"],
									 'version_major'=>$result["MOD_VERSIONMAJOR"],
									 'version_minor'=>$result["MOD_VERSIONMINOR"],
									 'revision'=>$result["MOD_VERSIONREV"],
									 'md5'=>$result["MOD_MD5"]);			
			}
			return json_encode(array("r"=>$modules));
		}
		
		public function resolveDependenciesDownwards($module){
			$con = $this->establishConection();
			$resultset = $con->query("select mod_id from modules
										where mod_name = ? and mod_versionmajor = ? and mod_versionminor = ? and mod_versionrev = ? and mod_md5 = ? ;",
										array($module->name, $module->version_major,$module->version_minor,$module->revision,$module->md5));
			if($result = $con->fetchArray($resultset)) {
				$modid = $result['MOD_ID'];
				$resultset = $con->query("select distinct dep_mod_dependson from dependencies where dep_mod_id = ?", array($modid));
				$moduleids = $modid;
				while($result = $con->fetchArray($resultset)) {
					do {
						$moduleids = $moduleids.",".$result["DEP_MOD_DEPENDSON"];
					} while ($result = $con->fetchArray($resultset));
					$resultset = $con->query("select dep_mod_dependson from dependencies where dep_mod_id in (" . $moduleids . ") and dep_mod_dependson not in (" . $moduleids . ")");
				}
				$resultset = $con->query("select mod_name, mod_displayname, mod_md5, mod_id, mod_versionmajor, mod_versionminor, mod_versionrev from modules where mod_id in (".$moduleids.") and mod_id != ".$modid);
				$modules = array();
				while($result = $con->fetchArray($resultset)){
					$modules[] = array('name'=>$result["MOD_NAME"],
										 'hrname'=>$result["MOD_DISPLAYNAME"],
										 'version_major'=>$result["MOD_VERSIONMAJOR"],
										 'version_minor'=>$result["MOD_VERSIONMINOR"],
										 'revision'=>$result["MOD_VERSIONREV"],
										 'md5'=>$result["MOD_MD5"]);	
				}
				return json_encode(array("r"=>$modules));
			}else{
				throw new Exception('Module does not Exist: '.$module->name);
			}
		}

		public function resolveDependenciesUpwards($module){
			$con = $this->establishConection();
			$resultset = $con->query("select mod_id from modules
										where mod_name = ? and mod_versionmajor = ? and mod_versionminor = ? and mod_versionrev = ? and mod_md5 = ? ;",
										array($module->name, $module->version_major,$module->version_minor,$module->revision,$module->md5));
			if($result = $con->fetchArray($resultset)) {
				$modid = $result['MOD_ID'];
				$resultset = $con->query("select distinct dep_mod_id from dependencies where dep_mod_dependson = ?", array($modid));
				$moduleids = $modid;
				while($result = $con->fetchArray($resultset)) {
					do {
						$moduleids = $moduleids.",".$result["DEP_MOD_ID"];
					} while ($result = $con->fetchArray($resultset));
					$resultset = $con->query("select dep_mod_id from dependencies where dep_mod_dependson in (" . $moduleids . ") and dep_mod_id not in (" . $moduleids . ")");
				}
				$resultset = $con->query("select mod_name, mod_displayname, mod_md5, mod_id, mod_versionmajor, mod_versionminor, mod_versionrev from modules where mod_id in (".$moduleids.") and mod_id != ".$modid);
				$modules = array();
				while($result = $con->fetchArray($resultset)){
					$modules[] = array('name'=>$result["MOD_NAME"],
										 'hrname'=>$result["MOD_DISPLAYNAME"],
										 'version_major'=>$result["MOD_VERSIONMAJOR"],
										 'version_minor'=>$result["MOD_VERSIONMINOR"],
										 'revision'=>$result["MOD_VERSIONREV"],
										 'md5'=>$result["MOD_MD5"]);	
				}
				return json_encode(array("r"=>$modules));
			}else{
				throw new Exception('Module does not Exist: '.$module->name);
			}
		}

		public function downloadModule($module){
			$con = $this->establishConection();
			$resultset = $con->query("select mod_name, mod_data, mod_displayname, mod_md5, mod_id, mod_versionmajor, mod_versionminor, mod_versionrev from modules 
									where mod_name = ? and mod_versionmajor = ? and mod_versionminor = ? and mod_versionrev = ? and mod_md5 = ? ;",
									array($module->name, $module->version_major,$module->version_minor,$module->revision,$module->md5));
			if($result = $con->fetchArray($resultset)) {
				$module = array('name'=>$result["MOD_NAME"],
							    'hrname'=>$result["MOD_DISPLAYNAME"],
						 	    'version_major'=>$result["MOD_VERSIONMAJOR"],
							    'version_minor'=>$result["MOD_VERSIONMINOR"],
							    'revision'=>$result["MOD_VERSIONREV"],
							    'md5'=>$result["MOD_MD5"]);
				return json_encode(array("r"=>$module,"data"=>base64_encode($result["MOD_DATA"])));
			}else{
				throw new Exception('Module does not Exist: '.$module->name);
			}
		}

		public function authenticate($password){
			$con = $this->establishConection();
			$res = $con->query("SELECT VALUE FROM CONFIG WHERE PARAM = 'password' OR PARAM = 'salt' ORDER BY PARAM ASC;");
			$set = $con->fetchObject($res);
			$password = $set->VALUE;
			$set = $con->fetchObject($res);
			$salt = $set->VALUE;
			$hash = hash('ripemd160', $password+$salt);
			
			$isValid = $password == $hash;
			$_SESSION['privileged'] = $isValid;
			return $isValid;
		}
		
		public function logout(){
			$_SESSION['privileged'] = false;
		}
		
		private function generateSalt(){
			$length = rand(128,255);
			for ($i = 0; $i < $length; $i++){
				$salt .= chr(rand(0,255));
			}
			return $salt;
		}
		
		private function checkAdmin(){
			if (!isset($_SESSION['privileged']) or !$_SESSION['privileged'])
				throw Exception('Only admin may perform this Operation (forgot to log on ?)');
		}
		
		public function changePassword($password){
			$this->checkAdmin();
				
			$con = $this->establishConection();
			$salt = $this->generateSalt();
			$hash = hash('ripemd160',$password+$salt);
			$con->query("UPDATE CONFIG SET VALUE = ? WHERE PARAM = ?", array($hash,'password'));
			$con->query("UPDATE CONFIG SET VALUE = ? WHERE PARAM = ?", array($salt,'salt'));
			return true;
		}
		
		public function uploadModule($data,$signature){
			include_once('Crypt/RSA.php');
			$con = $this->establishConection();
			
			$rsa = new Crypt_RSA();
			$rsa->setSignatureMode(CRYPT_RSA_SIGNATURE_PKCS1);
			$rsa->setHash('sha256');
			$rsa->setMGFHash('sha256');
			
			$res = $con->query("SELECT DEV_ID, DEV_NAME, DEV_PUBLICKEY FROM DEVELOPER;");
			$valid = false;
			$developerId = null;
			while($set = $con->fetchObject($res)){
				$rsa->loadKey($set->DEV_PULICKEY);
				$valid = $rsa->verify($data,$signature);
				if ($valid)
					$developerId = $set->DEV_ID;
					break;
			}
			if(!$valid)
				throw Exception('Signature verification Failed. Data has been manipulated.');
			
			mkdir(hash('md5',$signature));
			$file = fopen($signature.'.tar.gz','w');
			fwrite($file,$data);
			fclose();
			system('tar xfz '.$signature.'.tar.gz -C '.$signature.' > /dev/null');
			$manifestRaw = file_get_contents($signature."/manifest.json");
			if ($manifestRaw == false){
				throw Exception('Error while reading manifest');				
			}
			$manifest = json_decode($manifestRaw);
			if ($manifest == null){
				throw Exception('Manifest is not valid JSON');
			}
			$res = $con->query("SELECT MAX(MOD_VERSIONREV) AS MAXREVISION FROM MODULES WHERE MOD_NAME = ? ;",array($manifest->name));
			if ($set = $con->fetchObject($res)){
				$revision = ++$set->MAXREVISION;
			}else{
				$revision = 0;
			}
			$mod_id = $con->getSeqNext("MOD_GEN");
			$md5 = hash('md5',$data);
			$blobid = $con->createBlob($data);
			$con->query("INSERT INTO MODULES (MOD_ID, MOD_NAME, 
											MOD_DISPLAYNAME, 
											MOD_VERSIONMAJOR, 
											MOD_VERSIONMINOR,
											MOD_VERSIONREV,
											MOD_MD5,
											MOD_DATA)
									VALUES (?,?,?,?,?,?,?,?)",
									array($mod_id, $manifest->name,
										  $manifest->hrname, $manifest->version_major,
										  $manifest->version_minor, $revision, $md5, $blobid));
			$this->rrmdir($signature);
			unlink($signature.'.tar.gz');
			return true;
		}
		
		public function deleteModule($identifier,$major=null,$minor=null,$revision=null){
			$this->checkAdmin();
			$con = $this->establishConection();
			if (isset($major)){
				if (isset($minor)){
					if (isset($revision)){
						$con->query("DELETE FROM MODULES WHERE MOD_NAME = ? AND MOD_VERSIONMAJOR = ? AND MOD_VERSIONMINOR = ? AND MOD_VERSIONREV = ? ;"
									, array($identifier,$major,$minor,$revision));
					}else{
						$con->query("DELETE FROM MODULES WHERE MOD_NAME = ? AND MOD_VERSIONMAJOR = ? AND MOD_VERSIONMINOR = ? ;"
									, array($identifier,$major,$minor));	
					}
				}else{
				    $con->query("DELETE FROM MODULES WHERE MOD_NAME = ? AND MOD_VERSIONMAJOR = ? ;"
				    			, array($identifier,$major));
				}
			}else{
				$con->query("DELETE FROM MODULES WHERE MOD_NAME = ? ;"
				    			, array($identifier));
			}
			return true;
		}
		
		public function registerDeveloper($name, $fullname, $publickey){
			$this->checkAdmin();
			
			$devId = $con->getSeqNext("DEV_GEN");
			
			$con = $this->establishConection();
			$con->query("INSERT INTO DEVELOPERS (DEV_ID, DEV_NAME, DEV_FULLNAME, DEV_PUBLICKEY)
						 VALUES (?,?,?,?) ;", array($devId, $name, $fullname, $publickey));
			return true;
		}
		
		public function deleteDeveloper($devId){
			$this->checkAdmin();
			
			$con = $this->establishConection();
			$con->query("UPDATE DEVELOPERS SET DEV_PUBLICKEY = '' WHERE DEV_ID = ? ;");
			
			return true;	
		}
	}
?>