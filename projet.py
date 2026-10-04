import jeu

from gpiozero import Button
from gpiozero import RGBLED

jeu1 = jeu.jeu(3, Button(19), Button(20), Button(21), Button(13), Button(12), RGBLED(23, 24, 25), RGBLED(16, 17, 18))

jeu1.debut()

# python projet.py