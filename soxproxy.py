"""SOCKS proxy on demand (via Digitalocean)

Usage:
  soxproxy.py <token>
  soxproxy.py (-h | --help)

Help:
  <token>       Digitalocean account access token.

Options:
  -h --help     Show this screen.

"""


import digitalocean
import os
import subprocess
import time
import uuid

from docopt import docopt
from os.path import expanduser
from socket import *
from socket import AF_INET, SOCK_STREAM, timeout, error


DEFAULT_PUBLIC_KEY_NAME = "id_rsa.pub"
DEFAULT_PRIVATE_KEY_NAME = "id_rsa"
PREFIX = "SOCKSproxy-"
REDIRECTION_PORT = 8889


def msg(text):
  print " | ", text


class DoClient:
  manager = None  
  token = None

  def __init__(self, *args, **kwargs):
    self.token = args[0]
    self._auth()
    self.ssh_paths = {
      "key_name": self._make_key_name(),
      "public": "{0}/.ssh/{1}".format(expanduser("~"), DEFAULT_PUBLIC_KEY_NAME),
      "private": "{0}/.ssh/{1}".format(expanduser("~"), DEFAULT_PRIVATE_KEY_NAME),
    }

  def _auth(self):
    try:
      self.manager = digitalocean.Manager(token=self.token)
      self.manager.get_account()
    except digitalocean.baseapi.DataReadError as e:
      msg("")
      msg("Unable to authenticate you. Verify your token and try again.")
      msg("")
      exit(0)

  def _make_key_name(self):
    return "{0}{1}".format(PREFIX, uuid.uuid4())

  def _generate_public_by_private(self):
    public = subprocess.check_output(["ssh-keygen", "-y", "-f", "{0}".format(self.ssh_paths["private"])])
    msg("The generated public key is \n{0}".format(public))
    with open(self.ssh_paths["public"], "w") as pub:
      pub.write(public)        
    msg("And it saved into {0}".format(self.ssh_paths["public"]))

  def _generate_ssh_keypair(self):
    public = subprocess.call(["ssh-keygen", "-f", "{0}".format(self.ssh_paths["private"]), "-t", "rsa", "-N", ""])
    msg("Keys was generated!")
    
  def get_all_shh_keys(self):
    keys = self.manager.get_all_sshkeys()
    msg("Account keys:")
    for k in keys:
      msg(k.name)

  def genearate_ssh_pair(self):
    msg("Cooking SSH-keys")
    if not os.path.isfile(self.ssh_paths["public"]):
      if not os.path.isfile(self.ssh_paths["private"]):
        self._generate_ssh_keypair()
      else:
        msg("No public key was found... generating one")
        self._generate_public_by_private()
    else:
      msg("SSH keys are ready!")
      return True
    msg("SSH keys are ready!")

  def upload_ssh(self):
    user_ssh_key = open("{0}".format(self.ssh_paths["public"])).read()
    key = digitalocean.SSHKey(token=self.token,
                 name=self.ssh_paths["key_name"],
                 public_key=user_ssh_key)
    try:
      # If key already added in account
      key.create()
    except digitalocean.baseapi.DataReadError as e:
      msg("Public {0}".format(e.message))

  def show_droplets(self):
    msg("Your droplets are {0}".format(self.manager.get_all_droplets()))
  
  def whoami(self):
    msg("DO client name is {0}".format(self.name))

  def destroy_droplets(self):
    for droplet in self.manager.get_all_droplets():
      if droplet.name.startswith(PREFIX):
        msg("\tDestroying the droplet {0}".format(droplet.name))
        droplet.destroy()

  def create_droplet(self, sk):
    droplet = digitalocean.Droplet(token=self.token,
                               name="SOCKSproxy-{0}".format(uuid.uuid4()),
                               region='ams3', # Amster
                               image='ubuntu-16-04-x64', # Ubuntu 16.04 x64
                               size_slug='512mb',  # 512MB
                               ssh_keys=[sk], #Automatic conversion
                               backups=False)
    droplet.create()
    return droplet

  def create_SOKS_proxy_channel(self, ip):
    try:
      subprocess.call(["ssh", "-oStrictHostKeyChecking=no", "root@{0}".format(ip), "-D", "8889", "-N"])
    except KeyboardInterrupt as e:
      print "\n"
      msg("Now droplets with prefix {0} will be deleted on your account:".format(PREFIX))

  def wait_os_ready(self, ip):
    def ping():
      msg("\tTrying to ping {0}".format(ip))

      s = socket(AF_INET, SOCK_STREAM)
      s.settimeout(2)
    
      try:
        s.connect((ip, 22))      
      except (timeout, error) as e:
        s.close()
        return False        
      return True

    for i in xrange(20):
      if ping():
        return True
      else:
        time.sleep(1)
    raise Exception("Operation system doesn't loaded!!! Timeout!!!")


def main(token):
   c = DoClient(token)
   c.genearate_ssh_pair()
   c.upload_ssh()
   
   keys = c.manager.get_all_sshkeys()
   sk = None
   for key in keys:
     if key.name.startswith(PREFIX):
       sk = key
   droplet = c.create_droplet(sk)
   
   msg("Waiting for new droplet init:")
   # wait for instance ready
   exit = False
   for i in xrange(20):
     actions = droplet.get_actions()
     for action in actions:
       action.load()
       # Once it shows complete, droplet is up and running
       msg("\t" + action.status)
       if action.status == "completed":
         exit = True
         break
     if exit: break
     time.sleep(1)
   
   msg("Instance {0} is ready! Waiting for OS readiness:".format(droplet.name))

   droplet.load()
   ip = droplet.ip_address
   c.wait_os_ready(ip)

   msg("Now we create ip traffic redirect from localhost:{0} to remote host {1}".format(REDIRECTION_PORT, ip))
   msg("ATTENTION! Don't forget to press 'ctrl + c' when you will finish in order to avoid leave behind instance {0} in running state\n".format(droplet.name))

   c.create_SOKS_proxy_channel(ip)
   
   c.destroy_droplets()

   
if __name__ == "__main__":
  main(docopt(__doc__)["<token>"])

# TODO: parametrize everithing:
#       * droplet cteation - region, image, mgb etc
#       * ssh -v (verbose or not)
#       * proxy port
#       * destroy SOKSproxy- VMs
#       * retries in destroy + print msg if destroy can't be finished. User should delete VM by hands on web.  
