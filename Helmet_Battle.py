import pyxel
from math import sqrt
import random

import json
import os

class Joueur:
    def __init__(self):
        self.x = 50
        self.y = 128
        self.vitesse = 1.2
 
        self.ancienne_pos = (50,50)
        self.en_mouvement = False

        self.en_montant = False
        self.en_descendant = False
        self.acceleration = 15

        self.direction = 1 #droite
        self.sprite = (0,16)
        self.animation = 0
        self.animation_degat = False
        
        self.vie_max = 15
        self.vie = 15
        self.cooldown_pv = 0
        
        self.draw_dash = False
        self.cooldown_dash = 0
        self.force = 1
        self.cooldown_epee = 0

        self.argent = 0
        
        self.debut_saut = self.y
        self.debut_saut_x = self.x

        self.dash_x = self.x
        self.dash_y = self.y
        self.dash_direction = self.direction

        self.invincible = False
        self.decompte_invincible = 5

        self.renvoie_degats = False

        self.capacite = capacite()

        self.attaque_etat = False

        self.choix_arme = 0
        self.liste_choix_arme = False
        self.liste_arme = [epee((self.x,self.y)),Arc((self.x,self.y))]
        self.arme = self.liste_arme[0]
        

    def mouvement_joueur(self):
        self.ancienne_pos = (self.x,self.y)

        if pyxel.btn(pyxel.KEY_Q) and self.x >=0 and (not self.en_mouvement or self.direction == -1):
            self.x -= self.vitesse
            self.direction = -1
        if pyxel.btn(pyxel.KEY_D) and self.x <= 304 and (not self.en_mouvement or self.direction == 1):
            self.x += self.vitesse
            self.direction = 1
        
        if self.x < 0:
            self.x = 0
        elif self.x > 304:
            self.x = 304
        
        if self.ancienne_pos[0] != self.x:
            self.en_mouvement = True
        else:
            self.en_mouvement = False
        
    def animation_joueur(self):

        liste_sprite = [(0,16),(16,16),(32,16),(48,16)]          
           
        if self.cooldown_pv !=0 and pyxel.frame_count % 5 == 0:
                self.animation_degat = not self.animation_degat
        elif self.cooldown_pv ==0 and pyxel.frame_count % 5 == 0:
            self.animation_degat = False
        
        if self.en_mouvement == False:
            self.sprite = liste_sprite[0]
            self.animation = 1
        else:
            self.sprite = liste_sprite[self.animation]
            if pyxel.frame_count % 5 == 0:
                if self.animation == 3: 
                    self.animation = 1
                else:
                    self.animation += 1
                
            

    
    def saut(self):
        if pyxel.btnp(pyxel.KEY_SPACE) and self.en_montant == False and self.en_descendant == False:
            self.en_montant = True
            self.debut_saut = self.y
            self.debut_saut_x = self.x

        if self.en_montant == True: 
            self.vitesse = 1.8
            if self.debut_saut - self.y < 27:
                self.y -= self.acceleration
                self.acceleration = (sqrt(self.acceleration))
            else:
                self.en_descendant = True
                self.en_montant = False

        if self.en_descendant == True:
            self.y += self.acceleration
            self.acceleration = (self.acceleration**2)
          
        if self.y > 128:
            self.en_descendant = False
            self.vitesse =1.2
            self.acceleration = 15
            self.y = 128

    def dash(self,audio):
        if pyxel.btnp(pyxel.KEY_SHIFT) and self.cooldown_dash == 0:
            self.draw_dash = True
            self.x += 25 * self.direction
            self.dash_x = self.x
            self.dash_y = self.y
            self.dash_direction = self.direction
            self.cooldown_dash = 5
            audio.jouer_son("dash")

        if self.cooldown_dash > 0 and pyxel.frame_count % 20 ==0 :
            self.cooldown_dash -= 1
        if self.cooldown_dash == 4:
            self.draw_dash = False

    def cooldown_pv_updt(self):
        if self.cooldown_pv > 0 and pyxel.frame_count % 20 == 0:
            self.cooldown_pv -= 1

        if self.vie > self.vie_max:
            self.vie = self.vie_max

    def cooldown_invincibilite(self):
        if self.invincible and pyxel.frame_count % 30 ==0: 
            if self.decompte_invincible > 0:
                self.decompte_invincible -= 1
            else:
                self.invincible = False
                self.decompte_invincible = 5

    def cooldown_coup(self):
        if self.cooldown_epee > 0 and pyxel.frame_count % 2 ==0:
            self.cooldown_epee -= 1

    def changement_arme(self):
        if pyxel.btnp(pyxel.KEY_A) and self.liste_choix_arme:
            if not self.attaque_etat:
                if self.choix_arme ==0:
                    self.choix_arme = 1
                    self.arme = self.liste_arme[1]
                else: 
                    self.choix_arme = 0
                    self.arme = self.liste_arme[0]


    def attaque(self, ops,audio) :
        if self.arme.nom == "epee" or self.arme.nom == "epee_magique":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.cooldown_epee == 0:
                self.attaque_etat  = True
                self.cooldown_epee = 5
            else :
                self.attaque_etat = False

            if self.attaque_etat:
                audio.jouer_son("attaque")
                for mechant in ops :
                    if abs(self.arme.x - mechant.x) < 13 and abs(self.arme.y - mechant.y) < 4 and mechant.cooldown_pv ==0:
                        mechant.vie -= self.force*self.arme.degat
                        mechant.cooldown_pv = 2

                        if self.arme.nom == "epee_magique" and mechant.vie <=0:
                            if self.arme.cooldown_magie > 0:                     # charge attaque magique quand un ennemi meurt avec l'épée
                                self.arme.cooldown_magie -= 1

                        if self.x > mechant.x and mechant.name == "ops" :
                            mechant.x -= 12
                        elif mechant.name == "ops" :
                            mechant.x += 12
                        elif mechant.name == "mag":
                            mechant.tp = True

                
        if self.renvoie_degats:
            for mechant in ops:
                if abs(self.x_milieu() - mechant.x_milieu()) < 15 and abs(self.y_milieu() - mechant.y_milieu()) < 16 and mechant.cooldown_pv ==0:
                    mechant.vie -= 1
                    mechant.cooldown_pv = 2

                    if mechant.name == "mag":
                        mechant.tp = True


    
    def x_milieu(self):
        return self.x +8
    def y_milieu(self):
        return self.y +8
    def y_base(self):
        return self.y + 16

    def update(self,ops,audio):
        self.mouvement_joueur()
        self.animation_joueur()
        self.saut()
        self.dash(audio)
        self.cooldown_pv_updt()
        self.attaque(ops,audio)
        self.changement_arme()
        self.capacite.update(self,ops)
        self.cooldown_invincibilite()
        self.cooldown_coup()
        
        self.arme.update((self.x,self.y),self.direction)        
        if self.liste_arme[0].nom == "epee_magique":
            if self.liste_arme[0].attaque_mag != None:
                self.liste_arme[0].attaque_mag.update(ops)
        
        if self.liste_choix_arme:
            self.liste_arme[1].update_fleche(ops,self.force)
            
            

    def draw(self):
        self.capacite.draw(self)
        if self.draw_dash:
            pyxel.blt(self.dash_x+((-11)*self.dash_direction),self.dash_y,0,96,96,16*self.dash_direction,16,2)
        
        if self.invincible:
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1]+128,16*self.direction,16,2)
        else:
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2)

        if self.renvoie_degats:
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1]+144,16*self.direction,16,2)

        
        if self.animation_degat:
            pyxel.blt(self.x,self.y,0,79,32,16*self.direction,16,2)

        if self.arme.nom == "arc":
            self.arme.draw()
        else:
            self.arme.draw(self.attaque_etat)
        
        for fleche in self.liste_arme[1].fleches:
            fleche.draw()
        
        if self.liste_arme[0].nom == "epee_magique":
            if self.liste_arme[0].attaque_mag != None:
                self.liste_arme[0].attaque_mag.draw()
        
        

class capacite:
    def __init__(self):
        self.cap = []

        self.already_db_jump = False

        self.attente_bombe = 0
        self.bombe = None

        self.attente_potion = 0
    
    def double_saut(self,joueur):
        if joueur.en_descendant and not self.already_db_jump and pyxel.btnp(pyxel.KEY_SPACE):
            joueur.acceleration = 15
            joueur.debut_saut = joueur.y
            joueur.debut_saut_x = joueur.x
            joueur.en_montant = True
            joueur.en_descendant = False
            self.already_db_jump = True

        elif not joueur.en_montant and not joueur.en_descendant:
            self.already_db_jump = False

    def poser_bombe(self,joueur):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT) and self.bombe == None and self.attente_bombe == 0:
            self.bombe = bombe(joueur.x,joueur.y)
            self.attente_bombe = 5
        
        if self.attente_bombe > 0 and pyxel.frame_count % 100 ==0:
            self.attente_bombe -= 1
    def consommation_potion(self,joueur):
        if pyxel.btnp(pyxel.KEY_R) and self.attente_potion == 0:
            joueur.invincible = True
            self.attente_potion = 5
        
        if self.attente_potion > 0 and pyxel.frame_count % 120 == 0:
            self.attente_potion -= 1
    
    def update(self,joueur,ennemi):
        if "double_jump" in self.cap:
            self.double_saut(joueur)

        if "bombe" in self.cap:
            self.poser_bombe(joueur)
            if self.bombe != None:
                self.bombe.update(joueur,ennemi)
                if self.bombe.etat == "mort":
                    self.bombe = None
        
        if "potion_invincibilite" in self.cap:
            self.consommation_potion(joueur)

        
            
    
    def draw(self,joueur):
        if self.already_db_jump and joueur.en_montant:        
            pyxel.blt(joueur.debut_saut_x+1,joueur.debut_saut+14,0,64,104,16,8,2)
            pyxel.blt(joueur.x+7.5,joueur.y-4,0,80,96,16,16,2)
            pyxel.blt(joueur.x-6.5,joueur.y-4,0,80,96,-16,16,2)
        
        if self.bombe != None:
            self.bombe.draw()

class bombe:
    def __init__(self,x,y):
        self.x = x
        self.y = y-1

        self.etat = "posee"
        self.delai_expl = 3

        self.sprite = (64,64)

    def chute(self):
        if self.y < 131 and self.sprite!= (48,112):
            self.y += 2
            if self.y > 130:
                self.y = 130

    def activation_explosion(self,joueur,ennemis):
       if self.etat == "posee" and pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT):
          
           self.etat = "allumee"
           self.sprite= (64,112)
       
       elif self.etat == "allumee" and self.delai_expl > 0 and pyxel.frame_count % 50 ==0:
           self.delai_expl -= 1
        
       elif self.etat == "allumee" and self.delai_expl == 0:
           if self.sprite != (48,112):
                if abs(joueur.x_milieu() - (self.x+8)) < 32 and abs(joueur.y_milieu() - (self.y+8)) < 25 and self.sprite != (48,112) and not joueur.invincible:
                    joueur.vie -= 3
                    joueur.cooldown_pv = 5
                for ops in ennemis:
                    if abs(ops.x_milieu() - (self.x+8)) < 32 and abs(ops.y_milieu() - (self.y+8)) < 25 and self.sprite != (48,112):
                        ops.vie -= 3
                        ops.cooldown_pv = 5
                self.y -= 2
           self.sprite = (48,112)
           
           if pyxel.frame_count % 30 ==0:
               self.etat = "mort"
    
    def update(self,joueur,ennemis):
        self.chute()
        self.activation_explosion(joueur,ennemis)
    
    def draw(self):
        pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16,16,2)
        if self.sprite == (48,112): 
            pyxel.blt(self.x-28,self.y,0,48,128,16,16,2)
            pyxel.blt(self.x+28,self.y,0,64,128,16,16,2)

class Ops :
    def __init__(self,x_ops,y_ops,vitesse=1):
        self.name = "ops"

        self.x = x_ops
        self.y = y_ops
        self.vitesse = vitesse
        self.ancienne_pos = (50,50)
        self.en_mouvement = False
        
        self.cooldown_pv = 0
        self.vie = 5

        self.direction = -1 #gauche
        self.sprite = (64,16)
        self.animation = 0
        self.animation_degat = False
   
    def mouvement_ops(self, position_joueur):
        self.ancienne_pos = (self.x,self.y)
 
        if position_joueur[0] + 8 < self.ancienne_pos[0] :
            self.x -= self.vitesse
            self.direction = -1
        if position_joueur[0] - 8 > self.ancienne_pos[0] :
            self.x += self.vitesse
            self.direction = 1
       
        if self.ancienne_pos != (self.x,self.y):
            self.en_mouvement = True
        else:
            self.en_mouvement = False
 
    def animation_ops(self):
 
        liste_sprite = [(64,16),(80,16),(96,16),(112,16)]
        
        if self.cooldown_pv !=0 and pyxel.frame_count % 5 == 0:
                self.animation_degat = not self.animation_degat
        elif self.cooldown_pv ==0 and pyxel.frame_count % 5 == 0:
            self.animation_degat = False
            
        
        if self.en_mouvement == False:
            self.sprite = liste_sprite[0]
            self.animation = 1
        else:
            self.sprite = liste_sprite[self.animation]            
            if pyxel.frame_count % 5 == 0:
                if self.animation == 3: 
                    self.animation = 1
                else:
                    self.animation += 1

    def make_dammage(self,joueur,audio):
        if abs(joueur.x_milieu() - self.x_milieu()) < 10 and abs(joueur.y_milieu() - self.y_milieu()) < 10 and joueur.cooldown_pv ==0 and not joueur.invincible:
            joueur.vie -= 1
            audio.jouer_son("prise de dégats")
            joueur.cooldown_pv = 3
            

    def cooldown_pv_updt(self):
        if self.cooldown_pv > 0 and pyxel.frame_count % 20 == 0:
            self.cooldown_pv -= 1    
        
    def x_milieu(self):
        return self.x + 8

    def y_milieu(self):
        return self.y + 8

    def update(self, joueur,audio):
        self.mouvement_ops((joueur.x,joueur.y))
        self.animation_ops()
        self.make_dammage(joueur,audio)
        self.cooldown_pv_updt()
   
    def draw(self):
        pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2)
        if self.animation_degat:
            pyxel.blt(self.x,self.y,0,96,32,16*self.direction,16,2)

class Magicien:
    def __init__(self,x_ops,y_ops):
        self.name = "mag"

        self.x = x_ops
        self.y = y_ops
        self.vitesse = random.randint(10,20)/10
        self.ancienne_pos = (128,16)
        self.en_mouvement = False
        
        self.cooldown_pv = 0
        self.vie = 3

        self.tp = False
        self.frequence = random.randint(100,200)

        self.direction = -1 #gauche
        self.sprite = (128,16)
        self.animation_degat = False

        
        self.bdf = []
   
    def mouvement_mag(self, position_joueur):
        
        if self.tp:
            x = random.randint(10,300)
            if abs((x+8)-position_joueur[0]) > 24:
                self.x = x
                self.tp = False
                y = random.randint(0,1)
                if y ==0:
                    self.y = 128
                else:
                    self.y = 108
                

        if position_joueur[0] + 8 < self.x :
            self.direction = 1

        if position_joueur[0] - 8 > self.x:
            self.direction = -1

       

 
    def animation_mag(self):
        
        if self.cooldown_pv !=0 and pyxel.frame_count % 5 == 0:
                self.animation_degat = not self.animation_degat
        elif self.cooldown_pv ==0 and pyxel.frame_count % 5 == 0:
            self.animation_degat = False
            

    def make_dammage(self,joueur,audio):
        if abs(joueur.x_milieu() - self.x_milieu()) < 10 and abs(joueur.y_milieu() - self.y_milieu()) < 10 and joueur.cooldown_pv ==0 and not joueur.invincible:
            joueur.vie -= 1
            audio.jouer_son("prise de dégats")
            joueur.cooldown_pv = 3

    def lance_bdf(self):
        if pyxel.frame_count % self.frequence == 0:
            self.bdf.append(boule_de_feu(self))
        
        self.bdf = [boule for boule in self.bdf if boule.etat == "vie"]
            

    def cooldown_pv_updt(self):
        if self.cooldown_pv > 0 and pyxel.frame_count % 20 == 0:
            self.cooldown_pv -= 1    
        
    def x_milieu(self):
        return self.x + 8

    def y_milieu(self):
        return self.y + 8

    def update(self, joueur,audio):
        self.mouvement_mag((joueur.x,joueur.y))
        self.animation_mag()
        self.make_dammage(joueur,audio)
        self.cooldown_pv_updt()
        self.lance_bdf()
        for bdf in self.bdf:
            bdf.update(joueur,audio)
   
    def draw(self):
        pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2)
        if self.animation_degat:
            pyxel.blt(self.x,self.y,0,112,32,16*self.direction,16,2)

        for bdf in self.bdf:
            bdf.draw()
        

class boule_de_feu:

    def __init__(self,mag):
        self.x = mag.x
        self.y = mag.y
        self.vitesse = mag.vitesse

        self.etat = "vie"

        self.direction = -1 * mag.direction
        self.animation = 0

    def deplacement(self):
        if self.direction == -1:
            self.x -= self.vitesse
        else:
            self.x += self.vitesse

        if self.x > 334 or self.x < -10:
            self.etat = "mort"

    def make_damage(self,joueur,audio):
        if abs(joueur.x_milieu() - (self.x+7)) < 10 and abs(joueur.y_milieu() - (self.y+6)) < 10 and joueur.cooldown_pv ==0 and not joueur.invincible:
            joueur.vie -= 1
            audio.jouer_son("prise de dégats")
            joueur.cooldown_pv = 3
            self.etat = "mort"

    
    def animation_bdf(self):
        if pyxel.frame_count%3 ==0:
            if self.animation < 2:
                self.animation += 1
            else:
                self.animation = 0


    def update(self,joueur,audio):
        self.deplacement()
        self.make_damage(joueur,audio)
        self.animation_bdf()
    
    def draw(self):
        pyxel.blt(self.x,self.y,0,96+(16*self.animation),83,self.direction *14,11,2)

class attaque_magique:

    def __init__(self,epee):
        self.x = epee.x
        self.y = epee.y
        self.vitesse = 3.5

        self.etat = "vie"

        self.direction = epee.direction

    def deplacement(self):
        if self.direction == -1:
            self.x -= self.vitesse
        else:
            self.x += self.vitesse

        if self.x > 334 or self.x < -10:
            self.etat = "mort"

    def make_damage(self,ennemi):
        if abs(ennemi.x_milieu() - (self.x+7)) < 10 and abs(ennemi.y_milieu() - (self.y+6)) < 10 and ennemi.cooldown_pv ==0:
            ennemi.vie -= 2
            ennemi.cooldown_pv = 4
            if ennemi.name == "mag":
                ennemi.tp = True

    def update(self,ennemis):
        self.deplacement()
        for ops in ennemis:
            self.make_damage(ops)
    
    def draw(self):
        pyxel.blt(self.x,self.y,0,53,64,self.direction *8,16,2)


class fleche:

    def __init__(self,arc):
        self.x = arc.x + 4
        self.y = arc.y + 8
        self.vitesse = 5

        self.etat = "vie"

        self.direction = arc.direction
        self.degat = 1

    def deplacement(self,force):
        if self.direction == -1:
            self.x -= self.vitesse
        else:
            self.x += self.vitesse

        if self.x > 334 or self.x < -10:
            self.etat = "mort"

        self.degat = force

        

    def make_damage(self,ennemi):
        if abs(ennemi.x_milieu() - (self.x+7)) < 10 and abs(ennemi.y_milieu() - (self.y)) < 8 and ennemi.cooldown_pv ==0:
            ennemi.vie -= self.degat
            ennemi.cooldown_pv = 3
            if ennemi.name == "mag":
                ennemi.tp = True
            self.etat = "mort"

    def update(self,ennemis,force):
        self.deplacement(force)
        for ops in ennemis:
            self.make_damage(ops)
    
    def draw(self):
        pyxel.blt(self.x,self.y,0,132,72,self.direction *9,1,2)

class epee :
    def __init__(self, position_joueur):

        self.nom = "epee"
        self.x = position_joueur[0] 
        self.y = position_joueur[1]
 
        self.direction = 1 #droite
        self.sprite = (0,64)
        self.attaque = False
        self.degat = 1
 
    def position(self, position_joueur, orientation):
        self.y = position_joueur[1]
        self.direction = orientation
        if orientation == -1 :
            self.x = position_joueur[0] - 10
        else :
            self.x = position_joueur[0] + 10
    
    def update(self,position_joueur,orientation):
        self.position(position_joueur,orientation)

    def draw(self,attaque_joueur):
        if attaque_joueur:
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2, rotate = 45)
        else :
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2)

    
class epee_magique :
    def __init__(self, position_joueur):
        self.nom = "epee_magique"

        self.x = position_joueur[0] 
        self.y = position_joueur[1]
 
        self.direction = 1 #droite
        self.sprite = (16,64)
        self.cooldown_magie = 5
        self.attaque = False
        self.attaque_mag = None
        self.degat = 1
 
    def position(self, position_joueur, orientation):
        self.y = position_joueur[1]
        self.direction = orientation
        if orientation == -1 :
            self.x = position_joueur[0] - 13
        else :
            self.x = position_joueur[0] + 13

    def attaque_chargee(self):
        if self.cooldown_magie <= 0:
            self.sprite = (32,64)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_MIDDLE):
                self.attaque_mag = attaque_magique(self)
                self.cooldown_magie = 5
                self.sprite = (16,64)
        
        if self.attaque_mag != None:
            if self.attaque_mag.etat == "mort":
                self.attaque_mag = None
        

    def update(self,position_joueur,orientation):
        self.position(position_joueur,orientation)
        self.attaque_chargee()
        

    def draw(self,attaque):
        if attaque :
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2, rotate = 45)
        else :
            pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16*self.direction,16,2)
        
        

class Arc:

        def __init__(self, position_joueur):
            self.nom = "arc"

            self.x = position_joueur[0] 
            self.y = position_joueur[1]
    
            self.direction = 1 #droite
            self.sprite = 0
            self.cooldown_fleche = 0
            self.attaque = False
            self.fleches = []
    
        def position(self, position_joueur, orientation):
            self.y = position_joueur[1]
            self.direction = orientation
            if orientation == -1 :
                self.x = position_joueur[0] - 8
            else :
                self.x = position_joueur[0] + 8
    

        def tirer_fleche(self):
            if self.cooldown_fleche <= 0:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.attaque = True

                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                    if self.sprite == 2:
                        self.cooldown_fleche = 5
                        self.fleches.append(fleche(self))
                    self.attaque = False
                
            if pyxel.frame_count % 20 ==0:
                if self.attaque:
                    if self.sprite < 2:
                        self.sprite += 1
                else:
                    self.sprite = 0
                    
            
        def update_fleche(self,ennemis,force):
            self.fleches = [fleche for fleche in self.fleches if fleche.etat == "vie"]
            for fleche in self.fleches:
                fleche.update(ennemis,force)

            if self.cooldown_fleche > 0 and pyxel.frame_count % 10 == 0:
                
                self.cooldown_fleche -= 1
            

        def update(self,position_joueur,orientation):
            self.position(position_joueur,orientation)
            self.tirer_fleche()
            

        def draw(self):
            
            pyxel.blt(self.x,self.y,0,80+16*self.sprite,64,16*self.direction,16,2)
            
            
        




class Coffre:
    def __init__(self,x):
        self.x = x
        self.y = 128

        self.sprite = (32,32)
        self.type = random.randint(0,2)

        self.etat = "fermé"
        self.compteur_attente = None
    
    def interaction_joueur(self,joueur):
        if abs(joueur.arme.x+7 - (self.x + 8)) < 14 and abs(joueur.arme.y - (self.y + 8)) < 10 and joueur.attaque_etat and self.etat == "fermé":
            self.sprite = (48,32)
            self.etat = "ouvert"

    def ouverture_coffre(self,joueur):
        if self.etat == "ouvert" and abs(joueur.x_milieu() - (self.x + 8)) < 10 and abs(joueur.y_milieu() - (self.y + 8)) < 10 and pyxel.btnr(pyxel.KEY_E) and self.compteur_attente == None:
            self.compteur_attente = 3
            if self.type ==0:               # or
                joueur.argent += 10
            elif self.type == 1:               # force
                joueur.force += 0.25
            elif self.type == 2:               # pv
                joueur.vie += 3
            self.sprite = (64,32)


    def attente(self):
        if pyxel.frame_count % 40 ==0 and self.compteur_attente == 0:
            self.etat = "mort"
        elif self.compteur_attente != None and pyxel.frame_count % 40 == 0:
            self.compteur_attente -= 1
        
    

    def update(self,joueur):
        self.interaction_joueur(joueur)
        self.ouverture_coffre(joueur)
        self.attente()

    def draw(self):
        pyxel.blt(self.x,self.y,0,self.sprite[0],self.sprite[1],16,16,2)

        
        if self.type == 0 and self.etat == "fermé":               # or
            pyxel.blt(self.x,self.y-16,0,32,48,16,16,2)
        elif self.type == 1 and self.etat == "fermé":               # force
            pyxel.blt(self.x,self.y-16,0,96,48,16,16,2)
        elif self.type == 2 and self.etat == "fermé":               # pv
            pyxel.blt(self.x,self.y-16,0,112,48,16,16,2)

class boutique_bonus:
    def __init__(self,type_b,x):
        self.x = x
        self.y = 128

        self.type = type_b
        self.prix = self.init_prix()
        self.etat = True

    def selection_bonus(self,joueur):
        if self.etat and abs(joueur.x_milieu() - (self.x + 8)) < 10 and abs(joueur.y_milieu() - (self.y + 8)) < 10 and pyxel.btnr(pyxel.KEY_E) and self.type != 0 and joueur.argent >= self.prix:
            if self.type ==3:          
                joueur.liste_choix_arme = True
            elif self.type == 2:               
                joueur.liste_arme[0] = epee_magique((self.x,self.y))
                joueur.arme = joueur.liste_arme[0]
            elif self.type == 6:              
                joueur.capacite.cap.append("double_jump")
            elif self.type == 8:              
                joueur.vie_max = 25
                joueur.vie += 10
            elif self.type == 4:              
                joueur.capacite.cap.append("bombe")
            elif self.type == 5:              
                joueur.capacite.cap.append("potion_invincibilite")
            elif self.type == 7:              
                joueur.renvoie_degats = True
            elif self.type == 9:
                joueur.vitesse = 1.6
                joueur.force += 1 
            

            
            joueur.argent -= self.prix    
            
            self.etat = "mort"
        
    def init_prix(self):
        liste_prix = [0,0,50,30,25,25,20,35,25,20]
        return liste_prix[self.type]
    
    def update(self,joueur):
        self.selection_bonus(joueur)

    def draw(self):
        
        if self.type == 1:
            pyxel.blt(self.x,self.y-10,0,128,96,16,26,2)
        else:
            pyxel.blt(self.x,self.y,0,0,96,16,16,2)
            if self.type !=0:
               pyxel.blt(self.x+8,self.y-10,0,36,52,8,8,2)
               pyxel.text(self.x,120, str(self.prix),7)
        
        if self.type == 0:
            pyxel.blt(self.x,self.y,0,112,96,16,16,2)
        elif self.type == 3:               # arc
            pyxel.blt(self.x,self.y,0,96,64,16,16,2)
        elif self.type == 2:               # épée magique
            pyxel.blt(self.x,self.y,0,16,64,16,16,2)
        elif self.type == 6:               # double saut
            pyxel.blt(self.x,self.y,0,80,112,16,16,2)
        elif self.type == 8:               # + de vies
            pyxel.blt(self.x,self.y,0,112,48,16,16,2)
            pyxel.blt(self.x,self.y,0,112,112,16,16,2)
        elif self.type == 4: # bombes
            pyxel.blt(self.x,self.y,0,64,112,16,16,2)
        elif self.type == 5: # invincibilité
            pyxel.blt(self.x,self.y,0,16,48,16,16,2)
        elif self.type == 7: # renvoie degat corps à corps
            pyxel.blt(self.x,self.y,0,144,16,16,16,2)
        elif self.type == 9: # + force/ vitesse
            pyxel.blt(self.x,self.y,0,96,48,16,16,2)
        


class niveau :
    def __init__(self) :
        self.level = 1
        self.background = 0
        self.coffre = None
        self.coffre_select = None
        self.prst_boutique = False
        self.coffre_boutique = None
        self.prochain_niveau = False
 
        self.mettre_checkpoint = False
        self.put_checkpoint = False

        self.bonus_disponible = [0,1,2,3,4,5,6,7,8,9]

    

    def amelioration(self, ennemis, joueur):
        
        self.level += 1
        if self.background == 0 :
            self.background = 1
        else :
            self.background = 0
        for k in range(self.level) :
                if k % 5 == 0 and k != 0:
                    y = random.randint(0,1)
                    if y ==0:
                        y = 128
                    else:
                        y = 108
                    ennemis.append(Magicien(random.randint(100, 290), y))
                else:
                    ennemis.append(Ops(random.randint(200, 290), 128, random.randint(5, 10)/10))

        joueur.x = 70
        joueur.capacite.bombe = None

    def init_coffre(self,ennemis,joueur):
        if len(ennemis) == 0:
            if self.level % 3 == 0:
                if not self.prst_boutique:
                    self.prst_boutique = True
            else:
                self.prst_boutique = "fini"

            if self.prst_boutique == "fini" and self.coffre == None and pyxel.frame_count % 100 == 0:
                
                coord = random.randint(15, 200)
                self.coffre = [Coffre(coord), Coffre(coord + 32), Coffre(coord + 64)]


            
            if self.prochain_niveau and self.prst_boutique == "fini":
                if self.put_checkpoint:
                    self.mettre_checkpoint = True
                    self.put_checkpoint = False
                sauvegarder_record(self.level)
                self.amelioration(ennemis, joueur)
                self.coffre = None
                self.prst_boutique = False
                self.prochain_niveau = False
                

    def orga_coffre(self,joueur):

        if self.coffre != None:
            if pyxel.btnp(pyxel.KEY_C):
                self.put_checkpoint = True

            for chest in self.coffre:
                chest.update(joueur)
              
                if chest.etat == "mort":
                    self.prochain_niveau = True
                elif chest.etat == "ouvert":
                   self.coffre_select = chest
            
            if self.coffre_select != None:
                self.coffre = [self.coffre_select]
                self.coffre_select = None
    
    def orga_boutique(self,joueur):

        if self.prst_boutique == True:
            if self.coffre_boutique == None:
                self.coffre_boutique = [boutique_bonus(self.bonus_disponible[2],15),boutique_bonus(self.bonus_disponible[3],45),boutique_bonus(self.bonus_disponible[4],75),boutique_bonus(self.bonus_disponible[5],105),boutique_bonus(self.bonus_disponible[6],135),boutique_bonus(self.bonus_disponible[7],165),boutique_bonus(self.bonus_disponible[8],195),boutique_bonus(self.bonus_disponible[9],225),boutique_bonus(1,280)]
            else:
                for bonus in self.coffre_boutique:
                    bonus.update(joueur)

                    if bonus.etat == "mort":
                        if bonus.type != 1:
                            self.bonus_disponible[bonus.type] = 0
                        self.prst_boutique = "fini"

                if self.prst_boutique == "fini":
                    self.coffre_boutique = None



            




    def update(self, ennemis, joueur):
        self.init_coffre(ennemis, joueur)
        self.orga_coffre(joueur)
        self.orga_boutique(joueur)
        
class audio:
    def __init__(self):
        self.son_0 = pyxel.sounds[0].speed = 30 # musique nuit
        self.son_1 = pyxel.sounds[1].speed = 30 # musique jour
        self.son_2 = pyxel.sounds[2].speed = 7 # son de dash
        self.son_3 = pyxel.sounds[3].speed = 30 # son de frappe de l'arme
        self.son_3 = pyxel.sounds[4].speed = 7 # son de prise de dégats

    def jouer_son(self, action):
        self.action = action
        if self.action == "attaque":
            pyxel.play(0, 3, 0, False)
        elif self.action == "prise de dégats":
            pyxel.play(0, 4, 0, False)
        elif self.action == "dash":
            pyxel.play(0, 2, 0, False)


class Bouton:
    def __init__(self,nom,coordonnees,taille):
        self.x = coordonnees[0]
        self.y = coordonnees[1]

        self.longueur = taille[0]
        self.largeur = taille[1]

        self.nom = nom

        self.etat = False

    def interaction(self):
        if abs(pyxel.mouse_x - self.x_milieu()) < (self.longueur/2) and abs(pyxel.mouse_y - self.y_milieu()) < (self.largeur/2) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.etat = True
            


    def x_milieu(self):
        return self.x + (self.longueur/2)
    
    def y_milieu(self):
        return self.y + (self.largeur/2)
        
    def update(self):
        self.interaction()

    def draw(self):
        pass
            

        
class Menu:
    def __init__(self):
        self.in_menu = True

        self.bouton_menu = False

        self.mettre_pause = False
        self.commande = False

        self.boutons = [Bouton("Nouvelle",(127,103),(65,9)),Bouton("Continuer",(119,119),(81,9)),Bouton("Regles",(135,135),(49,9)),Bouton("Credit",(135,151),(49,9))]

        self.bouton_echap = Bouton("ESCP",(272,16),(31,31))
        self.bouton_lancer_derniere_save = Bouton("Save",(55,95),(209,72))

    def escp(self):
        if self.bouton_echap.etat:
            self.bouton_echap.etat = False
            if self.bouton_menu:
                for bouton in self.boutons:
                    bouton.etat = False

                self.bouton_menu = False
            else:
                pyxel.quit()
            
    
    def pause(self):
        if pyxel.btnp(pyxel.KEY_M):
            self.mettre_pause = not self.mettre_pause
            self.commande = False

        if self.mettre_pause and pyxel.btnp(pyxel.KEY_C):
            self.commande = not self.commande

        if self.mettre_pause and not self.commande and pyxel.btnp(pyxel.KEY_N):
            self.mettre_pause = False
            self.in_menu = True
            self.record = montrer_record()

    def menu_nouvelle_partie(self):
        if self.boutons[0].etat:
            self.in_menu = False

    def menu_continuer(self):
        if self.boutons[1].etat:
            self.bouton_menu = True

    def menu_credit(self):
        if self.boutons[3].etat:
            self.bouton_menu = True
    
    def menu_regles(self):
        if self.boutons[2].etat:
            self.bouton_menu = True
            

    def update(self):
        if self.in_menu:
            if not self.bouton_menu:
                for boutons in self.boutons:
                    boutons.update()
                
                self.menu_nouvelle_partie()
                self.menu_credit()
                self.menu_regles()
                self.menu_continuer()
            else:
                if self.boutons[1].etat:
                    self.bouton_lancer_derniere_save.update()
                    if self.bouton_lancer_derniere_save.etat:
                        self.bouton_menu = False
                        self.boutons[1].etat = False
                        self.in_menu = False
            self.bouton_echap.update()
            self.escp()
        else:
            self.pause()

    def draw_en_commande(self):
        pyxel.text(30,40,"DEPLACEMENT/INTERRACTION",8)
        pyxel.text(30,60,"DROITE : D",7)
        pyxel.text(30,70,"GAUCHE : Q ",7)
        pyxel.text(30,80,"SAUT : ESPACE ",7)
        pyxel.text(30,90,"DASH : MAJ",7)
        pyxel.text(30,100,"RECUPERER COFFRE : E",7)

        pyxel.text(170,40,"ATTAQUE/CAPACITE",8)
        pyxel.text(170,60,"ATTAQUE EPEE/ARC : CLIC GAUCHE",7)
        pyxel.text(170,70,"ATTAQUE MAGIQUE : CLIC MOLETTE ",7)
        pyxel.text(170,80,"CHANGER ARME : A",7)
        pyxel.text(170,90,"BOMBE : CLIC DROIT RELACHE ",7)
        pyxel.text(170,100,"POTION : R",7)

        pyxel.rect(95, 120, 110, 45, 14)
        pyxel.rect(100, 125, 100 , 35, 15)
        pyxel.rectb(100, 125, 100 , 35, 0)

        pyxel.text(125,135,"RETOUR : C",0)
        pyxel.text(110,150,"CONTINUER PARTIE : M ",0)

    def draw_en_pause(self,joueur,niv):
        pyxel.text(130,90,"PV : " + str(joueur.vie)+"/"+str(joueur.vie_max),8)
        pyxel.text(130,70,"Frc : " + str(joueur.force),13)
        pyxel.text(130,60,"Niveau " + str(niv),15)
        pyxel.text(130,80,"Or : " + str(joueur.argent),10)

        pyxel.rect(95, 120, 110, 60, 14)
        pyxel.rect(100, 125, 100 , 50, 15)
        pyxel.rectb(100, 125, 100 , 50, 0)

        pyxel.text(125,135,"COMMANDES : C",0)
        pyxel.text(110,150,"CONTINUER PARTIE : M ",0)
        pyxel.text(110,165,"RETURNER AU MENU : N" ,0)

    def draw_en_menu(self):
        for boutons in self.boutons:
            boutons.draw()

    def draw_menu_credit(self):
        pyxel.bltm(0,0,2,576,0,320,190)
    
    def draw_regle(self):
        pyxel.bltm(0,0,2,1024,0,320,190)

    def draw_continuer(self):
        pyxel.bltm(0,0,2,1472,0,320,190)


    def draw_menu_bouton(self):

        if self.boutons[1].etat:
            self.draw_continuer()

        elif self.boutons[2].etat:
            self.draw_regle()

        elif self.boutons[3].etat:
            self.draw_menu_credit()


    def draw(self,joueur,niv):
        if self.mettre_pause:
            pyxel.cls(0)
            pyxel.text(137,16,"PAUSE",7)
            if not self.commande:
                self.draw_en_pause(joueur,niv)
            else:
                self.draw_en_commande()

        
      

class App:

    def __init__(self):
        pyxel.init(320, 190, title="NDC calvin thibault 2025")
        pyxel.load("2.pyxres")
    
        self.menu = Menu()   
        self.joueur = Joueur()
        self.niveau = niveau()
        self.ops = [Ops(280,128,0.7)]
        self.audio = audio()
        self.checkpoint_restant = 3

        self.liste_sprite_bonus = [(0,64),(96,64),(64,112),(16,48),(80,112),(144,16),(112,48),(96,48)]
        self.bonus_en_attente = [False,False,False,False,5]

        self.record = montrer_record()

        pyxel.run(self.update, self.draw)

    
    def etat_bonus(self):

        if self.niveau.bonus_disponible[2] == 0:
            if self.joueur.liste_arme[0].cooldown_magie > 0:
                self.liste_sprite_bonus[0] = (16,64)                  # epee magique
                self.bonus_en_attente[4] = self.joueur.liste_arme[0].cooldown_magie
            else:
                self.liste_sprite_bonus[0] = (32,64)
                self.bonus_en_attente[4] = False


        if self.joueur.cooldown_epee > 0:   
            self.bonus_en_attente[0] = self.joueur.cooldown_epee                
        else:
            self.bonus_en_attente[0] = False
        
        if self.joueur.liste_arme[1].cooldown_fleche > 0:
            self.liste_sprite_bonus[1] = (80,64)    
            self.bonus_en_attente[1] = self.joueur.liste_arme[1].cooldown_fleche                 # arc
        else:
            self.liste_sprite_bonus[1] = (96,64)
            self.bonus_en_attente[1] = False

        if self.joueur.capacite.attente_bombe > 0:
            self.liste_sprite_bonus[2] = (64,64)          
            self.bonus_en_attente[2] = self.joueur.capacite.attente_bombe          # bombe
        else:
            self.liste_sprite_bonus[2] = (64,112)
            self.bonus_en_attente[2] = False

        if self.joueur.capacite.attente_potion > 0:
            self.liste_sprite_bonus[3] = (0,48)       
            self.bonus_en_attente[3] = self.joueur.capacite.attente_potion    # potion
        else:
            self.liste_sprite_bonus[3] = (16,48)
            self.bonus_en_attente[3] = False

        if self.joueur.capacite.attente_potion > 0:
            self.liste_sprite_bonus[3] = (0,48)       
            self.bonus_en_attente[3] = self.joueur.capacite.attente_potion    # potion
        else:
            self.liste_sprite_bonus[3] = (16,48)
            self.bonus_en_attente[3] = False
        
    def checkpoint(self):
        if self.niveau.mettre_checkpoint:
            self.niveau.mettre_checkpoint = False
            ajouter_checkpoint(self)    
    
    def utilisation_historique(self):
        
        dico = utiliser_checkpoint()
        if dico != False:
            self.joueur.x = dico["joueur_x"]
            self.joueur.vie = dico["joueur_vie"]
            self.joueur.vie_max = dico["joueur_vie_max"]
            self.joueur.force = dico["joueur_force"]
            self.joueur.vitesse = dico["joueur_vitesse"]
            self.joueur.direction =  dico["joueur_direction"]
            self.joueur.argent = dico["joueur_argent"]
            self.joueur.renvoie_degats = dico["joueur_renvoie_degat"]
            self.joueur.choix_arme = dico["joueur_choix_arme"]
            self.joueur.liste_choix_arme = dico["joueur_liste_choix_arme"]
            self.niveau.level = dico["level"] -1
            self.niveau.background = dico["background"]
            self.niveau.bonus_disponible = dico["bonus_dispo"]
            if dico["bonus_dispo"][2] == 0:
                self.joueur.liste_arme[0] = epee_magique((self.joueur.x,self.joueur.y))
                self.joueur.arme = self.joueur.liste_arme[0]
                self.joueur.liste_arme[0].cooldown_magie = dico["cooldown_magie"]
                
          
            if dico["double_jump"] == 1:
                self.joueur.capacite.cap.append("double_jump")
            if dico["potion"] == 1:
                self.joueur.capacite.cap.append("potion_invincibilite")
            if dico["bombe"] == 1:
                self.joueur.capacite.cap.append("bombe")

            self.ops = []

            self.niveau.amelioration(self.ops, self.joueur)
            self.niveau.coffre = None
            self.niveau.prst_boutique = False
            self.niveau.prochain_niveau = False


    def update(self):
        if not self.menu.in_menu:
            if not self.menu.mettre_pause and self.joueur.vie > 0:
                self.etat_bonus()
                self.joueur.update(self.ops,self.audio)

                for opponent in self.ops:
                    opponent.update(self.joueur,self.audio)
                self.ops = [opponent for opponent in self.ops if opponent.vie > 0]
                
                self.niveau.update(self.ops,self.joueur)
                self.checkpoint()
            
            

        if self.joueur.vie > 0 or self.menu.in_menu :
            self.menu.update()
        else:
            if pyxel.btnp(pyxel.KEY_N):
                self.menu.in_menu = True
                reinitialiser_checkpoint()
                self.record = montrer_record()

        if self.menu.boutons[0].etat:
            self.joueur = Joueur()
            self.niveau = niveau()
            self.ops = [Ops(280,128,0.7)]

            self.liste_sprite_bonus = [(0,64),(96,64),(64,112),(16,48),(80,112),(144,16),(112,48),(96,48)]
            self.bonus_en_attente = [False,False,False,False,5]
            self.menu.boutons[0].etat = False
            reinitialiser_checkpoint()

        if self.menu.bouton_lancer_derniere_save.etat:
            self.menu.bouton_lancer_derniere_save.etat = False
            self.utilisation_historique()
    
    def draw(self):
        if not self.menu.in_menu:
            pyxel.mouse(False)
            if self.joueur.vie > 0:

                if not self.menu.mettre_pause:
                    pyxel.bltm(0,0,self.niveau.background,0,0,320,190)
                    pyxel.text(280,20,"PV : " + str(self.joueur.vie)+"/"+str(self.joueur.vie_max),7)
                    pyxel.text(280,10,"Niveau " +str(self.niveau.level),7)
                    pyxel.text(280,30,"Or : " + str(self.joueur.argent),7)
                    pyxel.text(280,40,"Frc : " + str(self.joueur.force),7)

                    pyxel.text(5,10,"PAUSE : M ",7)

                    if self.niveau.coffre != None:
                        pyxel.text(5,20,"POSER CHECKPOINT : C ",7)

                    if self.niveau.put_checkpoint:
                        pyxel.text(23,60,"RECUPEREZ UN COFFRE ET COMMENCEZ LA PROCHAINE MANCHE POUR SAUVEGARDER !",7)

                    
                    for k in range(8):
                        
                        espace = 100+k*16
                        if k > 3:
                            espace += 40
                        


                        if k > 0 and self.niveau.bonus_disponible[k+2] != 0:
                            pyxel.rect(espace, 8, 16, 16, 13)
                            pyxel.rectb(espace, 8, 16, 16, 0)
                            pyxel.blt(espace,8,0,self.liste_sprite_bonus[k][0],self.liste_sprite_bonus[k][1],16,16,2)
                            pyxel.blt(espace,8,0,112,96,16,16,2)
                            
                        else:
                            
                            if k < 4:
                                pyxel.rect(espace, 8, 16, 16, 15)
                                if self.bonus_en_attente[k] != False:
                                    pyxel.rect(espace, 8, 16, self.bonus_en_attente[k]*(16/5), 13)
                                else:
                                    pyxel.rect(espace, 8, 16, 16, 15)
                                pyxel.rectb(espace, 8, 16, 16, 0)
                            elif k == 4:

                                if self.joueur.en_descendant and not self.joueur.capacite.already_db_jump:
                                    pyxel.rect(espace, 8, 16, 16, 15)
                                else:
                                    pyxel.rect(espace, 8, 16, 16, 13)

                                pyxel.rectb(espace, 8, 16, 16, 0)
                            else:
                                pyxel.rect(espace, 8, 16, 16, 15)
                                pyxel.rectb(espace, 8, 16, 16, 0)

                            pyxel.blt(espace,8,0,self.liste_sprite_bonus[k][0],self.liste_sprite_bonus[k][1],16,16,2)


                    pyxel.rect(188, 8, 16, 16, 15)
                    if self.joueur.cooldown_dash != 0:
                        pyxel.rect(188, 8, 16, self.joueur.cooldown_dash*(16/5), 13)      # dash
                    else:
                        pyxel.rect(188, 8, 16, 16, 15)
                    pyxel.rectb(188, 8, 16, 16, 0)
                    pyxel.blt(188,8,0,96,112,16,16,2)
                    
                    
                    if self.niveau.bonus_disponible[2] == 0:
                        if self.bonus_en_attente[4] == False:
                            pyxel.rect(100, 5, 16, 2, 8)
                        else:
                            pyxel.rect(100, 5, 16, 2, 13)
                            pyxel.rect(100, 5, (5-self.bonus_en_attente[4])*(16/5), 2, 9)



                    if self.niveau.coffre != None:
                        for chest in self.niveau.coffre:
                            if chest.compteur_attente != None:
                                pyxel.text(110,80,"Prochaine manche dans : " + str(chest.compteur_attente),7)
                        
                    if self.niveau.coffre != None:
                        for chest in self.niveau.coffre:                
                            chest.draw()

                    if self.niveau.coffre_boutique != None:
                        for bonus in self.niveau.coffre_boutique:
                            bonus.draw()
            
                    for opponent in self.ops:
                        opponent.draw()
                    
                    self.joueur.draw()

                else:
                    self.menu.draw(self.joueur,self.niveau.level)


                
            else:
                pyxel.cls(0)
                pyxel.text(140,90,"GAME OVER",7)
                pyxel.text(140,110,"Niveau " + str(self.niveau.level),7)
                pyxel.text(140,120,"Or : " + str(self.joueur.argent),7)
                pyxel.text(140,150,"MENU : N",7)
        
        else:
            pyxel.mouse(True)
            if not self.menu.bouton_menu:
                pyxel.bltm(0,0,2,0,0,320,190)
                self.menu.draw_en_menu()
                pyxel.text(127,81.5,"RECORD : " +  self.record,8)
            else:
                self.menu.draw_menu_bouton()


########### GESTION DE L'HISTORIQUE ##########################################################################################

# Chemin du fichier
HISTORIQUE_FICHIER = "historique.txt"

def charger_historique():
    """
    Charge les trajets précédemment enregistrés dans le fichier 'historique.txt'.
    Si le fichier n'existe pas encore, retourne une liste vide.

    Retourne :
        - Une liste de dictionnaires, chacun représentant un trajet déjà calculé,
          avec les clés : 'depart', 'arrivee', 'chemin' et 'distance'.
    """
    if os.path.exists(HISTORIQUE_FICHIER):
        # Ouvre le fichier en lecture avec l'encodage UTF-8
        with open(HISTORIQUE_FICHIER, "r", encoding="utf-8") as f: # pas besoin de fermer le fichire car "with"
            # Lit et convertit le contenu JSON en liste Python
            return json.load(f)
    
    # Si le fichier n'existe pas, on retourne un historique vide
    return []

def montrer_record():
   
    # Charge les trajets déjà enregistrés
    historique = charger_historique()
    
    if len(historique) == 0:
        return "Niveau X"
    else:
        return "Niveau " + str(historique[0])
    
def sauvegarder_record(record):
    """
    Ajoute un nouveau trajet dans le fichier 'historique.txt' si celui-ci n'existe pas encore.

    Paramètres :
        record : int
    """
    # Charge les trajets déjà enregistrés
    historique = charger_historique()
    
    if len(historique) ==0:
        historique.append(record)

    elif record > historique[0]:
        historique[0] = record
    
    # Écrit l'historique complet (ancien + nouveau) dans le fichier, en JSON
    with open(HISTORIQUE_FICHIER, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def reinitialiser_checkpoint():

    # Charge les trajets déjà enregistrés
    historique = charger_historique()
    
    if len(historique) > 0:
     historique = [historique[0]]
    
    # Écrit l'historique complet (ancien + nouveau) dans le fichier, en JSON
    with open(HISTORIQUE_FICHIER, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def ajouter_checkpoint(partie):
  
    
    # Charge les trajets déjà enregistrés
    historique = charger_historique()
    
    dico = {
             "joueur_x" : partie.joueur.x,
             "joueur_vie": partie.joueur.vie,
             "joueur_vie_max": partie.joueur.vie_max,
             "joueur_force": partie.joueur.force,
             "joueur_vitesse": partie.joueur.vitesse,
             "joueur_direction": partie.joueur.direction,
             "joueur_argent" : partie.joueur.argent,
             "joueur_renvoie_degat": partie.joueur.renvoie_degats,
             "joueur_choix_arme": partie.joueur.choix_arme,
             "joueur_liste_choix_arme": partie.joueur.liste_choix_arme,
             "double_jump": 0,
             "bombe": 0,
             "potion": 0,
             "level": partie.niveau.level,
             "background": partie.niveau.background,
             "bonus_dispo": partie.niveau.bonus_disponible,
             "cooldown_magie": 5
            }

    if "bombe" in partie.joueur.capacite.cap:
        dico["bombe"] = 1
    
    if "potion_invincibilite" in partie.joueur.capacite.cap:
        dico["potion"] = 1

    if "double_jump" in partie.joueur.capacite.cap:
        dico["double_jump"] = 1

    if partie.joueur.liste_arme[0].nom == "epee_magique":
        dico["cooldown_magie"] = partie.joueur.liste_arme[0].cooldown_magie

    if len(historique) > 1:
      historique[1]= dico
    else:
        historique.append(dico)


    # Écrit l'historique complet (ancien + nouveau) dans le fichier, en JSON
    with open(HISTORIQUE_FICHIER, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def utiliser_checkpoint():
    # Charge les trajets déjà enregistrés
    historique = charger_historique()
    if len(historique) > 1:
        return historique[1]
    else:
        return False


App()


# python -m pyxel edit F:\nuit_du_code_2025_thibault_calvin\2.pyxres
