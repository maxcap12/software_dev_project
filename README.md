## How to use:
```bash
git clone git@github.com:maxcap12/software_dev_project.git
```

run the server:
```bash
python3 server.py
```

run twice (one for each player):
```bash
python3 client.py
```

## How to play:

#### Placing phase:
```
place \<ship> \<x> \<y> <H|V>
```
available ships: Carrier (size 5), Battleship (4), Cruiser (3), Submarine (3), Destroyer (2), the uppercase is needed

x and y: coordinated of the start of the ship

H for horizontal placement, V for vertical

Once all the ships are placed: 
```
ready
```

#### Game phase:
```
fire <x> <y>
```
