ReColor your Anki desktop to whatever aesthetic you like! Combine with the <a href="https://ankiweb.net/shared/info/1210908941">Custom Background and Gear Icon add-on</a> for an amazing look!

# How to Use
- Download from [AnkiWeb](https://ankiweb.net/shared/info/688199788)
    - This add-on has been tested for Anki 2.1.41+ up to 2.1.50. It may work on older versions, but it has NOT been tested and we can't provide support for that at the moment.
- After installing, there will be an AnKing menu at the top. Click the ReColor submenu to open the ReColor dialog
- The colors listed are everything that Anki customizes (unfortunately some things are linked together so changing one will change the other and there's no way around that for us)
- Once you click "Save", the colors will update. 
- Click "Advanced" if you want to input html colors or see the underlying code


<b>Share your pictures with #ReColorAnKing and tag @AnKingMed on social media so we can re-share it!</b>

## Screenshots
<b>See other examples users have uploaded or upload your own theme: <a href="https://github.com/AnKingMed/AnkiRecolor/wiki">link</a></b>
<img width="600px" src="https://github.com/AnKingMed/AnkiRecolor/blob/main/screenshots/solaris_light.png?raw=true">
<img width="600px" src="https://github.com/AnKingMed/AnkiRecolor/blob/main/screenshots/nord_dark.png?raw=true">
<img width="600px" src="https://github.com/AnKingMed/AnkiRecolor/blob/main/screenshots/one_darkest.png?raw=true">
<img width="600px" src="https://github.com/anarchy1923/AnkiRecolor/blob/main/screenshots/everforestDark.png?raw=true">

# Development

To update icons_rc.py file after changes to [icons.qrc](src/addon/AnKing/icons.qrc), run the following command, then edit the file to add `-> None` type hint.
```bash
pyrcc5 ./src/addon/AnKing/icons.qrc -o ./src/addon/icons_rc.py
```

## Tests & Formatting
This project uses [mypy](https://github.com/python/mypy) type checking for Python, and [standardjs](https://github.com/standard/standard) for formatting Javascript.

```
python -m mypy .
npx standard --fix
```

You will need to install the following python packages to run mypy: 
```
python -m pip install aqt PyQt5-stubs mypy
```

This project doesn't use a strict python formatter. Even so, please make it look pretty enough :)


### If you like these, please consider donating to this project

<center><div style="vertical-align:middle;"><a href="https://www.theanking.com"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/TheAnKing-New.png?raw=true"></a></div></center>

<center>&nbsp;<a href="https://www.facebook.com/ankingmed"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/FB.png?raw=true"></a>
<a href="https://www.instagram.com/ankingmed"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/Instagram.png?raw=true"></a>
<a href="https://www.youtube.com/theanking"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/YT.png?raw=true"></a>
<a href="https://www.tiktok.com/@ankingmed"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/TikTok.png?raw=true"></a>
<a href="https://www.twitter.com/ankingmed"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/Twitter.png?raw=true"></a></center>

<div><center><a href="https://www.theanking.com/vip"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/Patreon.jpg?raw=true"></a></center></div>



<div><center><a href="https://courses.theanking.com"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/MasteryCourse.png?raw=true"></a></center></div>
