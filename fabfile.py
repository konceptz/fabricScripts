from fabric.api import *

#user input, can be switched to a file in for faster access
GIT_NAME = prompt("Enter full Git Target (ex:http://github.com/username/newsite.git) :")
REMOTE_PATH = prompt("Enter full path to create at target(s) (ex: /var/www) :")
#GIT_NAME = 'http://github.com/konceptz/clientpdp.git'
#REMOTE_PATH = '/var/new/site'
"""
def deploy():
	base_config()
	with settings():
		sudo("apt-get install git -y")
		sudo("mkdir -p %s" % REMOTE_PATH)
		with cd(str(REMOTE_PATH)):
			sudo("git clone %s" % GIT_NAME)
			sudo("git remote add upstream %s" % GIT_NAME)
			sudo("git fetch upstream")
			sudo("git merge upstream/master")
"""
def base_config():
	#env.sudo_user = 'arthurhinds'
	#env.password = 'computer1'
	sudo_user = prompt("Enter Sudo Username on remote target(s) :")
	env.password = prompt("enter passwd:")

def update():
	git_command = prompt("Enter git command to execute against target(s) (ex: git commit -m ""Bug smushed"") :")
	base_config()
	with settings(sudo_user='arthurhinds'):
		with cd(str(REMOTE_PATH)):
			sudo(str(git_command))
			
	


"""
def checkSSHAccess():



def isReady():
	checkVMs()
	checkCon()

def checkVMs():
	print ("checking VMs")

def checkCon():
	print ("checking internet con")
"""

