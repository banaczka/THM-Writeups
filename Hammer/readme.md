# Hammer

## Recon

Nmap scan:

```bash
sudo nmap -sS -p- -T5 -vvvv 10.10.241.150
```

We found 2 open ports, 22 and 1337. The first one is SSH, and the second is a web server.

After connecting to http://10.10.241.150:1337/ we are presented with a login form.. Providing invalid credentials don't give any clues about usernames or passwords.

In the page source, we find a note:

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

II ran a quick test by adding an `X-Forwarded-For` header with value of `127.0.0.1` and send a request. In reponse i got header `Rate-Limit-Pending` with the reset value. We can try to write a Python script, which every 7 tries would change the `X-Forwarded-For` to `127.0.0.2`, `127.0.0.3` and so on. However, with this method we have limited success rate, as the token is valid for 180 seconds, so we need to be quick.

In repo is python script to brute force the code.

It found correct code, we need to paste a PHPSESSID to our browser, change password and login. After that, we receive first flag.

## JWT and RCE

We are now on `dashboard.php` site, there is form asking us to type a command, but our session has been ended quickly.

Looking at the source, there's a JavaScript snippet that checks if `persistentSession` cookie is true. We can just use Burp Suite and investigate from there.

By capturing login request we see, that there are 3 cookies, PHPSESSID, token and persistentSession. Let's look at the token cookie, it's a JWT.

We also see form asking us to execute a command, capture this request and play with it from burp suite. Seems that the only working command is `ls`, but we see the file with `.key` extension.

Looking at the token we can see, that it has `HS256` algorithm and has a parameter kid (Key ID) with value `/var/www/mykey.key`. Also we have a role assigned, which is "user".

From what we know, directory `hmr_logs` is in the same folder, as our `.key` file. We should try to access it from a URL:

```
http://10.10.232.105:1337/file.key
```

We downloaded a `.key` file, let's check its content. We can try to make a new token, changing key path, role to "admin" and make a signature with found key.

Go to jwt.io website, paste there our token, change `kid` to `/var/www/html/file.key` and `role` to `admin`, eventually verify the signature using the obtained key.

It should look similarily to this:

```json
{
  "typ": "JWT",
  "alg": "HS256",
  "kid": "/var/www/html/file.key"
}

{
  "iss": "http://hammer.thm",
  "aud": "http://hammer.thm",
  "iat": 1742565568,
  "exp": 1742569168,
  "data": {
    "user_id": 1,
    "email": "tester@hammer.thm",
    "role": "admin"
  }
}

HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  hash
)
```

Once we have a new token, paste it into `Authorization: Bearer` header and send a new request from burp. Now, we can execute commands like `whoami`, `cat` and get a second flag.