# Hammer

## Recon

Nmap scan:

```bash
sudo nmap -sS -p- -T5 -vvvv 10.10.241.150
```

We found 2 open ports, 22 and 1337. The first one is SSH, and the second is a web server.

After connecting to http://10.10.241.150:1337/ we have a login form. Providing invalid credentials don't give any clues about usernames or passwords.

In source code we found a note:

```html
<!-- Dev Note: Directory naming convention must be hmr_DIRECTORY_NAME -->
```

We can try to find some directories. First, prepare a file with valid names and then launch gobuster:

```bash
sed 's/^/hmr_/' /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt > prefixedlist.txt
gobuster dir -u http://10.10.241.150:1337 -w prefixedlist.txt
```

We found directory `hmr_logs`, and file `error.logs` inside. In file is information, that user `tester@hammer.thm` used wrong password, that means that this user already exists.

## Reset password bypassing

Let's try reset his password. After we submit his email, we got a form where we need to provide a 4-digit code, which is valid for 180 seconds.

After 8 tries, we got a message, that rate limit has been exceeded.

However, after we deleted PHPSESSID cookie, we can reset password again.

Also, we found a reponse header, `Rate-Limit-Pending: 8`, which decrements after every unsuccessful try.

I made a little test, I added `X-Forwarded-For` header with value of `127.0.0.1` and send a request. In reponse i got header `Rate-Limit-Pending` with reseted value. We can try to write a Python script, which every 7 tries would change the `X-Forwarded-For` to `127.0.0.2`, `127.0.0.3` and so on. However, with this method we have limited success rate, as the token is valid for 180 seconds, so we need to be quick.

Finally, I managed to write a code, it is in this repo.

It found correct code, we need to paste a PHPSESSID to our browserm change password and login. After that, we receive first flag.

