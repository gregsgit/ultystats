# Stats json format

A stats json file looks like

```
{ "game" : {
    "home" : "Huckagenerians",
    "versus" : "KitKat",
    "date" : "9/15/2017",
	"abbrevs": {"letter" : "name", ...},
    "plays" : [
	...
	]
  }
}
```

"abbrevs" are used so that I can enter single characters for player
names, and they will be expanded in final version.

## Plays

Each play is one of:

1. 'V' all by itself, representing the other team scoring
2. a "note" object in the form { "note" : "string"}
3. 'T' meaning a timeout
4. a sequence of throws

Each element in a sequence of throws is one of:

1. "D-name", to start a sequence, means "name" made a defensive play
   to regain possession. 
2. "name", a player receiving, and then throwing, the disk. 
3. "X", to finish a sequence, means the name immediately preceding
   threw it away (bad throw). 
4. "name-D", to end a sequence, means the throw (from the preceding
   name) was reasonably good, but "name" dropped it.
5. "name-!", to end a sequence, means "name" scored by receiving a
   throw in the endzone. 

Examples:

* `[D-Adam, Debbie, Chris, ...]` means Adam made D, Debbie picked up
  and threw to Chris 
* `[D-Adam, Adam, X]` then means Adam made D then threw it away
* `[D-Adam, Adam, X], {"note: "Adam was throwing to Debbie"}` then
  means Adam made D then tried to throw to Debbie but throw was
  incomplete. 
* `[..., Debbie, Adam-!]` means Debbie threw to Adam for score
* `[..., Debbie, Adam-D]` means Debbie threw a decent throw to Adam,
  but Adam dropped it.

