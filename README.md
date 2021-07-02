*Marek Bečvář*

# MovieLib_Desktop

Desktop movie viewing library for my hard drive.

Moved from pyglet to curses! LOOKS COOL! 

## About
Get movie info and cover pictures from IMDB and display them neatly with Curses and Ueberzug. 

Let's you search through all of the them, sort them (alphabetic, score sort).

### Controls
You may use vim-type inputs for searching.

| `Input` | `Action` |
|---------|----------|
| j | Move down |
| k | Move up |
| g / G | Move to first/last |
| S | Switch sorts (alphab., score) |
| ENTER | Play |
| / | Switch to/from SEARCH input mode |

### Running
To make the application work properly with your movie names you need to rename them to <br>
`<Movie name> <year of release>;<anything>.<any video format>` (it will prompt you when searching through them and find them in unwante name format).

The app still needs folder `movieData` located somewhere in the dir with the executable (storing pics+info). 
