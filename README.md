ReColor your Anki desktop to whatever aesthetic you like! Combine with the <a href="https://ankiweb.net/shared/info/1210908941">Custom Background and Gear Icon add-on</a> for an amazing look!

# How to Use
- Download from [AnkiWeb](https://ankiweb.net/shared/info/688199788)
    - This add-on has been tested for Anki 2.1.41+ up to 2.1.50. It may work on older versions, but it has NOT been tested and we can't provide support for that at the moment.
- After installing, there will be an AnKing menu at the top. Click the ReColor submenu to open the ReColor dialog
- The colors listed are everything that Anki customizes (unfortunately some things are linked together so changing one will change the other and there's no way around that for us)
- Once you click "Save", the colors will update. 
- Click "Advanced" if you want to input html colors or see the underlying code


<b>Share your pictures with #ReColorAnKing and tag @AnKingMed on social media so we can re-share it!</b>

## Community themes
- [Nord](themes/nord.json) by [u/Various_Breadfruit48](https://www.reddit.com/r/Anki/comments/t2y9xx/nord_theme_for_anki_using_the_awesome_recolor/?utm_source=share&utm_medium=web2x&context=3)
  - Dark theme
    ![image](https://user-images.githubusercontent.com/73290412/155923384-284d958a-39a6-4428-b88b-25c965942042.png)
  
  - Light theme
    ![image](https://user-images.githubusercontent.com/73290412/155977209-efa344d9-d467-451f-a063-0142187f934a.png)

- [Solarized dark](themes/solarized-dark.json) by [u/No_Walk9711](https://www.reddit.com/r/Anki/comments/t2lkb3/dark_mode_solarized_anki_theme_using_recolor_addon/?utm_source=share&utm_medium=web2x&context=3)
  ![image](https://user-images.githubusercontent.com/73290412/155923721-0e297593-a32d-440a-aed2-fa490b445cf2.png)
 
- [Solarized light](themes/solarized-light.json) by [u/BlueGreenMagick](https://www.reddit.com/r/Anki/comments/t1w1gz/solarized_anki_theme_using_recolor_addon/?utm_source=share&utm_medium=web2x&context=3)
  ![image](https://user-images.githubusercontent.com/73290412/155923938-a13e185b-782c-48db-9eb9-c2488cca398c.png)

# Development
## Setup
After cloning the project, run the following command
```bash
git submodule update --init --recursive
```
The command installs [ankiaddonconfig](https://github.com/BlueGreenMagick/ankiaddonconfig/) as a git submodule.

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

# Building ankiaddon file
After cloning the repo, go into the repo directory and run the following command to install the git submodule [ankiaddonconfig](https://github.com/BlueGreenMagick/ankiaddonconfig/)
```
git submodule update --init src/addon/ankiaddonconfig
```
After installing the git submodule, run the following command to create an `recolor.ankiaddon` file
```
cd src/addon ; zip -r ../../recolor.ankiaddon * ; cd ../../
```

### If you like these, please consider donating to this project

<p align="center">
<a href="https://www.ankingmed.com" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/AnKingSmall.png?raw=true"></a><a href="https://www.ankingmed.com" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/TheAnKing.png?raw=true"></a>
  <br>
  <a href="https://www.facebook.com/ankingmed" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/FB.png?raw=true"></a>     <a href="https://www.instagram.com/ankingmed" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/Instagram.png?raw=true"></a>     <a href="https://www.youtube.com/theanking" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/YT.png?raw=true"></a>     <a href="https://www.tiktok.com/@ankingmed" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/TikTok.png?raw=true"></a>     <a href="https://www.twitter.com/ankingmed" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/Social/Twitter.png?raw=true"></a>
  <br>
<a href="https://www.ankipalace.com/membership" rel="nofollow"><img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/Patreon.jpg?raw=true"></a>
<br>
<b>Check out our Anki Mastery Course! (The source of funding for this project)</b><br>
          <a href="https://courses.ankipalace.com/?utm_source=anking_bg_add-on&amp;utm_medium=anki_add-on_page&amp;utm_campaign=mastery_course" rel="nofollow">https://courses.ankipalace.com</a>
<a href="https://courses.ankipalace.com/?utm_source=anking_bg_add-on&amp;utm_medium=anki_add-on_page&amp;utm_campaign=mastery_course" rel="nofollow">
  <br>
  <img src="https://raw.githubusercontent.com/AnKingMed/My-images/master/AnKing/AnkiPalace.png?raw=true"></a></p>
