# Foobartory

## Resume (in french)

Le but est de coder une chaîne de production automatique de `foobar`.

On dispose au départ de 2 robots, mais on souhaite accélérer la production pour prendre le contrôle du marché des `foobar`.
Pour ce faire on va devoir acheter davantage de robots, le programme s'arrête quand on a 30 robots.

Les robots sont chacun capables d'effectuer les activités suivantes :

- Miner du `foo` : occupe le robot pendant 1 seconde. 
- Miner du `bar` : occupe le robot pendant un temps aléatoire compris entre 0.5 et 2 secondes. 
- Assembler un `foobar` à partir d'un `foo` et d'un `bar` : occupe le robot pendant 2 secondes.
  L'opération a 60% de chances de succès ; en cas d'échec le `bar` peut être réutilisé, le `foo` est perdu. 
- Vendre des `foobar` : 10s pour vendre de 1 à 5 `foobar`, on gagne 1€ par `foobar` vendu 
- Acheter un nouveau robot pour 3€ et 6 `foo`, 0s 

A chaque changement de type d'activité, le robot doit se déplacer à un nouveau poste de travail, cela l'occupe pendant 5s. 

_Notes_:

- 1 seconde du jeu n'a pas besoin d'être une seconde réelle.
- Le choix des activités n'a pas besoin d'être optimal (pas besoin de faire des maths), seulement fonctionnel.

## Install and run

### With Poetry

Have Poetry installed, python 3.9 and clone the project

Install the project (creation of en .venv)

```
poetry install
```

Run the application

```
poetry run foobartory 
```

### Without Poetry

No need to install a venv as the program only use standard packages

Run the application
```
python foobartory 
```


## How does it work?

In this project, I used asyncio to simulate robots that work separately.

A robot is a class instance inherited by Robot: different classes for different action.
When a robot starts to `work()`, it creates an async task which loop forever de to its action. 

At the start of the application, three tasks are launched:
- logger : logger frequently the stock and assignment status
- manager : here to check if there are newly created robots and assign them to a role.
  Stop the program when 30 robots have been created
- init_step : the goal of this task is to move robot on different roles as long as there is less than 5 robots available 

## Notes

A change of role is done by the deletion of a robot and the creation of another one with the desired role.

It's possible to see the production of foo and bar with logging in DEBUG mode.