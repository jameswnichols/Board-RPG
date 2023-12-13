# Board RPG
A 2D randomly-generated game made for my Year 1 Semester 1 programming project.

### Features:
- Has an island map which changes each time you play.
- Grindy and basic gameplay loop.

### How To Play:
1. Use `show board` to see your surroundings.
1. Use `show inv` to see your inventory.
1. Select your axe with `select` followed by its number.
1. Use `face` with a compass direction to look around.
1. Use `move f` to take your first step!
1. Use `cut` to chop your first tree `♣`, given you are looking at it and have the appropriate tool selected.
1. Open your inventory to see the wood you collected!
1. Alternatively, you could find the nearest Goblin `♀` and attack it with `attack`.
1. Collect resources to `trade` with villagers `♙`, found near houses `⌂` in villages.
1. Make your way to the centre of the island, fighting and collecting on the way!
1. Defeat the final boss to win...

### Commands:
(Optional args start with `+`'s and possible args are separated with `|`'s)
- `show` > `board` | `inv / inventory`, `+page[1 -> ...]` | `help`, `+page[1 -> ...]`
- `move` > `+f / for / forwards` | `+b / back / backwards` | `+l / left` | `+r / right`, `+steps[1 -> ...]`
- `dir / face` > `n` | `ne` | `e` | `se` | `s` | `sw` | `w` | `nw`
- `equip / select` > `slot[1 -> ...]`
- `save` > `[filename]`
- `load` > `[filename]`
- `i / interact / cut / mine / trade / attack / med`
- `rendermap` > *Renders the map to a file called "map.txt".*
- `giveall` > *CHEAT - Gives yourself 1000 of every item in the game*.

## Restrictions:
- Only allowed to have one `main.py` file.
- Not allowed to use `continue`, `break`, `class`, `global` or `pass`.
- Not allowed `while` loops that don't have terminating conditions.
- Can only make functions that modify the `state` variable, can't modify it outside of them.
- Must contain a `main()` function.
- Must contain a `show_board()` function that **doesn't** change `state`.
