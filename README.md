# DOSOCKSProxy
One-click cheap SOCKsProxy server on Digitalocean

Install
```
$ virtualenv .venv && pip install requirements.txt

(.venv)$ python soxproxy.py -h
```

How to use:
1. Create account on Digitalocean
2. Generate access token
3. Run the script
```
(.venv)$ python soxproxy.py <do_token>
 |  Cooking SSH-keys
 |  SSH keys are ready!
 |  Public SSH Key is already in use on your account
 |  Waiting for new droplet init:
 |  	in-progress
 |  	in-progress
 |  	in-progress
 |  	in-progress
 |  	in-progress
 |  	in-progress
 |  	completed
 |  Instance SOCKSproxy-1f706950-4052-4b66-8cd1-64ea9ca8e943 is ready! Waiting for OS readiness:
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  	Trying to ping 128.199.55.230
 |  Now we create ip traffic redirect from localhost:8889 to remote host 128.199.55.230
 |  ATTENTION! Don't forget to press 'ctrl + c' when you will finish in order to avoid leave behind instance SOCKSproxy-1f706950-4052-4b66-8cd1-64ea9ca8e943 in running state

Warning: Permanently added '128.199.55.230' (ECDSA) to the list of known hosts.
^C

 |  Now droplets with prefix SOCKSproxy- will be deleted on your account:
 |  	Destroying the droplet SOCKSproxy-1f706950-4052-4b66-8cd1-64ea9ca8e943
```
4. Open your browser and turn on using proxy.
```
Proxy host: 127.0.0.1
Proxy port: 8889
```
5. Serf the internet. Your traffic will be redirected to remote machine.


What really script do?:
1. Upload ssh public key on your do account.
2. Create cheapest droplet and get their ip.
3. Wait when OS became ready.
4. Create ssh tunnel (SOCKs5) to that droplet.
5. Delete the droplet after usage.

Money.

Main case of using that proxy is to reach blocked internet resources by providing ip from another country.
Start and delete instance on DO during 1 hour costs $0.01.

Tested only on Ubuntu 16.04.
If you want to add windows support - you are welcome.

