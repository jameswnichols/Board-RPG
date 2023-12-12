# Board RPG
A 2D randomly-generated game made for my Year 1 Semester 1 programming project.

### Features:
- Has an island map which changes each time you play.
- Grindy and basic gameplay loop.

### Commands (Optional args start with `+`'s and possible args are separated with `|`'s):
- `show` > `board` | `inv / inventory`, `+page[1 -> ...]` | `help`, `+page[1 -> ...]`
- `move` > `+f / for / forwards` | `+b / back / backwards` | `+l / left` | `+r / right`, `+steps[1 -> ...]`
- `dir / face` > `n` | `ne` | `e` | `se` | `s` | `sw` | `w` | `nw`
- `equip / select` > `slot[1 -> ...]`
- `save` > `[filename]`
- `load` > `[filename]`
- `interact / cut / mine / trade`
- `rendermap` > *Renders the map to a file called "map.txt".*
- `giveall` > *CHEAT - Gives yourself 1000 of every item in the game*.

## Restrictions:
- Only allowed to have one `main.py` file.
- Not allowed to use `continue`, `break`, `class`, `global` or `pass`.
- Not allowed `while` loops that don't have terminating conditions.
- Can only make functions that modify the `state` variable, can't modify it outside of them.
- Must contain a `main()` function.
- Must contain a `show_board()` function that **doesn't** change `state`.
