import time
import math
import random
from time import sleep

from gpiozero import LED
from gpiozero import Button
from gpiozero import RGBLED
from RPLCD.i2c import CharLCD 

class jeu():
    def __init__(self, nb_tour:int, btnR:Button, btnG:Button, btnB:Button, btn1:Button, btn2:Button, rgb1:RGBLED, rgb2:RGBLED):
        self.tour = nb_tour
        self.btnR = btnR
        self.btnG = btnG
        self.btnB = btnB
        self.btn1 = btn1
        self.btn2 = btn2
        self.RGBjoueur = rgb1
        self.RGBjeu = rgb2

        self.lcd = CharLCD('PCF8574', 0x27)
        self.diff = 0
        self.intensite = 1
        self.essai = 0
        self.positif = True
        self.pause = True

    # Choisir une couleur aléatoire et l'afficher sur la lumière RGB du jeu
    def choix(self):
        code = [0, 0, 0]

        while True:
            for i in range(3):
                code[i] = (math.floor(random.random()*(self.diff + 1))) / self.diff

            if not code == [0, 0, 0]:
                break

        self.RGBjeu.color = (code[0], code[1], code[2])
        self.pause = False

    # Vérifier que les bonnes lumières soient allumées
    def verifier(self):
        lum = 0

        if (self.RGBjeu.red == self.RGBjoueur.red):
            lum += 1
        if (self.RGBjeu.green == self.RGBjoueur.green):
            lum += 1
        if (self.RGBjeu.blue == self.RGBjoueur.blue):
            lum += 1

        return lum

    def off(self):
        self.RGBjeu.off()
        self.RGBjoueur.off()

    # APPUIS

    # Appuyer le premier bouton (vert)
    def appui1(self):
        self.btn1.when_pressed = None
        self.pause = True

        if self.diff == 0:
            self.diff = 1
            self.intensite = 1

        sleep(0.1)
        self.btn1.when_pressed = self.appui1

    # Appuyer le deuxième bouton (jaune)
    def appui2(self):
        self.btn2.when_pressed = None

        if self.diff > 0:
            # commande abs() : http://www.w3schools.com/python/ref_func_abs.asp
            if self.positif:
                self.intensite = -abs(self.intensite)
                self.positif = False

                print("Mode négatif activé.")
            else:
                self.intensite = abs(self.intensite)
                self.positif = True

                print("Mode positif activé.")
        else:
            self.diff = 2
            self.intensite = 0.5

        sleep(0.1)
        self.btn2.when_pressed = self.appui2

    # Appuyer une des boutons de couleurs
    def appuiRGB(self, couleur):
        if not self.pause:
            self.btnR.when_pressed = None
            self.btnG.when_pressed = None
            self.btnB.when_pressed = None

            if couleur == "R" and self.RGBjoueur.red + self.intensite >= 0 and self.RGBjoueur.red + self.intensite <= 1:
                self.RGBjoueur.red += self.intensite
            elif couleur == "G" and self.RGBjoueur.green + self.intensite >= 0 and self.RGBjoueur.green + self.intensite <= 1:
                self.RGBjoueur.green += self.intensite
            elif couleur == "B" and self.RGBjoueur.blue + self.intensite >= 0 and self.RGBjoueur.blue + self.intensite <= 1:
                self.RGBjoueur.blue += self.intensite
            #print(couleur)
            print(self.RGBjoueur.color)
            sleep(0.1)
            self.btnR.when_pressed = lambda b, couleur="R",:self.appuiRGB(couleur)
            self.btnG.when_pressed = lambda b, couleur="G":self.appuiRGB(couleur)
            self.btnB.when_pressed = lambda b, couleur="B":self.appuiRGB(couleur)
        else:
            print("Soyez patient.")
        
    # SCÈNES

    # Début de la partie
    def debut(self):
        self.btn1.when_pressed = self.appui1
        self.btn2.when_pressed = self.appui2

        self.lcd.clear()
        print("")
        print("* Presser le premier bouton (vert) pour sélectionner la difficulté Facile.")
        print("* Presser le deuxième bouton (jaune) pour sélectionner la difficulté Difficile.")

        while True:
            self.lcd.write_string("Vert : Facile")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Jaune : Difficile")

            if self.diff > 0:
                break

        print("")

        decompte = 3
        while decompte > 0:
            self.lcd.clear()
            self.lcd.write_string("Debut du jeu")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(f"dans {decompte} {'secondes' if decompte > 1 else 'seconde'}")
            print(f"La partie débute dans {decompte} {'secondes.' if decompte > 1 else 'seconde.'}")
            decompte -= 1
            sleep(1)

        print("")
        print("")
        print("")
        print("##### DÉBUT DE LA PARTIE ! #####")
        print("")
        print("But : reproduire la même couleur que la lumière à côté de la votre, déjà allumée.")
        print("")
        print(f"Configuration : nombre de tours : {self.tour}")
        print("")
        print("Les boutons Rouge, Bleu et Vert changent les couleurs.")
        print("Presser le premier bouton (vert) pour valider votre couleur.")
        print("Presser le deuxième bouton deuxième pour alterné entre le mode augmenté / réduire l'intensité.")
        
        self.partie()
    
    # La partie
    def partie(self):
        self.btnR.when_pressed = lambda b, couleur="R":self.appuiRGB(couleur)
        self.btnG.when_pressed = lambda b, couleur="G":self.appuiRGB(couleur)
        self.btnB.when_pressed = lambda b, couleur="B":self.appuiRGB(couleur)

        for i in range(0, 3):
            self.choix()
            self.lcd.clear()
            self.lcd.write_string("Vert : Valider")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Jaune : (-/+)")
            sleep(1)
            self.pause = False

            while True:
                if self.pause:
                    lum = self.verifier()

                    if lum == 3:
                        self.off()
                        self.lcd.clear()
                        self.lcd.write_string("Bonne reponse !")

                        print("")
                        print("Bonne réponse !")
                        print("")
                        sleep(2)
                        break
                    else:
                        self.essai += 1
                        self.lcd.clear()
                        self.lcd.write_string("Mauvaise reponse.")
                        self.lcd.cursor_pos = (1, 0)
                        self.lcd.write_string(f"{lum}/3 lumieres")

                        print(f"{self.RGBjoueur.color}Mauvaise réponse.")
                        print(f"{self.RGBjoueur.color}Votre lumière RGB à {lum} lumière(s){self.RGBjeu.color} ayant la bonne intensité.")
                        print("")
                        sleep(2)
                        self.pause = False
        
        self.fin()

    # Fin de la partie
    def fin(self):
        print("")
        print("")
        print("Fin de la partie.")
        print(f"Vous avez faite {self.essai} erreur(s).")

        self.lcd.clear()
        self.lcd.write_string(f"Fin du jeu")
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(f"Erreur(s) : {self.essai}")