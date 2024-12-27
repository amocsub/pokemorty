# Solution

The only two tools needed to solve the challenge can be used on websites.

1. [GCHQ - CyberChef](https://gchq.github.io/CyberChef "CyberChef")
2. [FutureBoy - Steganography Tools](https://futureboy.us/stegano/ "Steganography Tools")
3. [Google Image Search](https://www.google.es/imghp "Google Image Search")

## Stage 1
At the begining you should find a binnary code that can be decoded with [GCHQ - CyberChef](https://gchq.github.io/CyberChef "CyberChef") that give you a hint to go to a [/challenge](https://pokemorty.herokuapp.com/challenge "challenge") site.

On that site you will find an image that was digitally modified and the code inside the image car plate is the one you should input to access the site. For that you will need to search on [Google Image Search](https://www.google.es/imghp "Google Image Search") to and find the digits missing (***PIKACHU***).

## Stage 2
At this point now you are on a login webpage that is susceptible to SQLi but to exploit this vulnerability perhaps you need more context of the DB so if you get a 404 on the page the error message that show up with a Mr. Meeseeks hides information about the database user table. There are hints to use [FutureBoy - Steganography Tools](https://futureboy.us/stegano/ "Steganography Tools") on the html and inside that image you will find the conformation of the table pokemon_masters that is the one with the information of login.

There if you try to exploit the username field with a SQLi you will find that the information retrieved is posted on the response body.

With some trials I've found that the best combination to retrieve all the DB table is:

```bash
curl --request POST \
  --url https://pokemorty.fly.dev/authenticate \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "username=' OR 1=1 --&password=asd"
```

With that query all the users and password's will be exported on the response body and with that information you will find that a specific user has the password in cleartext ***USER:morty;PASSWORD:ilovemyfamily***

## Stage 3
Once inside the pokedex you will find lot of pokemons, but keeping in mind the user list there was a username called ***RickSanchez*** but you can't retrieve his password, so there you have to abuse the cookies you have setted up. There is a cookie called ***master_id*** that is the one used to retrieve all the pokemons asociated, to give a hint on this the ***master_id*** of the user ***RickSanchez*** is ***130*** as ***C-130*** the earth number he comes from.

When you retrieve all the pokemons ***RickSanchez*** has you will find out he own's all of them, he is the onlyone with the 151 pokemons, so there you will find out that pokemon 130 is modified with ***RickSanchez*** face and inside that image is the flag, to retrieve it you should use again the [FutureBoy - Steganography Tools](https://futureboy.us/stegano/ "Steganography Tools") to decode the image and you will find out that is present in an ASCII art ***FLAG{I_LOVE_POKEMON}***.

## Validate Flag
To validate the flag go to the home page with the binary and post it there to send it to ***RickSanchez***

# MISC
There is another endpoint to reset the database in case someone drop down the service, just [click here](https://pokemorty.herokuapp.com/restore_database "restore_database") and if a __success__ show's up it was restored.