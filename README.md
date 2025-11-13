## Prints projected points per gameweek(s)

Log in at https://fantasy.premierleague.com/

Click your Points tab.

In the URL, the number right after /entry/ is your FPL Manager ID.
Example: https://fantasy.premierleague.com/entry/3273218/event/11 → ID is 3273218.

You need to have python3 installed, for MacOS:

```bash
brew install python3
```

Setup & Run

```bash
pip3 install requests
git clone https://github.com/adilet2306/fpl.git
cd fpl
python3 fpl.py
```
When prompted:

Enter your FPL Manager ID (press Enter to submit),

Then enter the gameweek(s) you want, e.g. 12 or 12,13.

The script will print projected points for each player in your team for the selected gameweek(s).
