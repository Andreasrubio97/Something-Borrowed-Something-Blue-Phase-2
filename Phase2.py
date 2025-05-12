import sqlite3
import random

conn = sqlite3.connect("immunity_data.db") # Connect to a database file (creates it if it doesn't exist)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS enemy_immunities (
    enemy_name TEXT NOT NULL,
    immune_to TEXT NOT NULL
)
""")

cur.execute("DELETE FROM enemy_immunities") # included so that my table when the program runs does not keep adding and adding(duplicates). My database starts fresh everytime

# enemies and their immunities. Previously a dictionary
enemies = [ 
    ("Xerxes", "Upper Cut"),
    ("Scipio", "Flame Thrower"),
    ("Nero", "Katana Sword"),
    ("Darth Sideburns", "Bicycle Kick"),
    ("Hannibal", "Elbow Swing"),
    ("Red Skull", "Flip Kick"),
    ("Jack the Ripper", "Elbow Swing"),
    ("Ozymandias", "Flame Thrower"),
    ("Thanos", "Katana Sword"),
    ("Caligula", "Bicycle Kick")
]


for enemy in enemies: # insert each enemy one at a time using a for loop
    cur.execute("INSERT INTO enemy_immunities (enemy_name, immune_to) VALUES (?, ?)", enemy)

conn.commit()
conn.close()


class Power_Abilities:
    def __init__(self):
        self.abilities = {
            "Upper Cut": 25,
            "Flip Kick": 25,
            "Bicycle Kick": 30,
            "Katana Sword": 35,
            "Flame Thrower": 30,
            "Elbow Swing": 20
        }

    def show_abilities(self): # created this function so that when called displays the power abilities and its damage level for selection
        for key, val in self.abilities.items():
            print(f"{key}: {val}")
    
    def get_damage(self, ability_name): # this function returns the value of the power ability. Its purpose is to use the value of the chosen power ability to substract from the enemies health in class fighter
        return self.abilities.get(ability_name, 0)
    
class Fighter:
    def __init__(self, name, attack=15, health=100): # instance variables depict the name of the fighters and the default variables (base levels)
        self.name = name
        self.attack = attack
        self.health = health
        self.power_abilities = Power_Abilities() # reference the power abilities class where each power ability has a higher damage level
        self.last_ability_used = None # initialize this as None to use later when the user attempts to utilize the same power ability consecutively

    def strike(self, target): # 'self' is the hero; 'target' is the enemy
        # this functions execute base attacks. # the self, is the hero hero.stricke() that is passed in when I call the function and target is the villain # hero.strike(villain)
        target.health -= self.attack
        target.health = max(target.health, 0) # prevent the healht from going below zero
        print(f"{self.name} hits {target.name} for {self.attack} damage. {target.name} has now {target.health} of health") 
        if target.health > 0: # as long as the villain is still alive they will hit back
            target.strike_back(self) # villains immediately strike back the hero after each attack
    
    def use_power_attack(self, target): # this function allows the user to choose which power attacks to use against the Enemies
        self.power_abilities.show_abilities() # calling on the show abilities function to show the user the options
        ability_name = input("Type Power Attack Exactly: ")
        if ability_name == self.last_ability_used: # this compares the ability being used with the one previously used. If it is True then user pays punishment
            print(f"You already used {ability_name} last time! You lose 10 health as punishment.")
            self.health -= 10 # user loses -10
            print(f"{self.name} now has {self.health} health.\n")
            return 
        damage = self.power_abilities.get_damage(ability_name) # calling on the get_damage function to ge the value from the name of the ability and inserting the value in damage.
        if damage > 0: # if the name that is input is correct then this will be true and thus operation will be performed after the next condition
            if target.is_immune(ability_name): # right before the operation happens, I need to assess whether the villain is immune to the ability name
                print(f"{target.name} is immune to {ability_name}! No damage dealt")
                target.strike_back(self) # 
                
            else:
                target.health -= damage # perform the operation 
                target.health = max(target.health, 0) # prevent the healht from going below zero
                print(f"{self.name} hits {target.name} for {damage} damage. {target.name} has now {target.health} of health") # prints the resulting values
                if target.health > 0: # I need this to make sure the enemy does not strick back when is dead
                    target.strike_back(self)

            self.last_ability_used = ability_name # variable self.last_ability_used gets updated from None to the actual ability used last.
        
        else: # if name is not input correctly then default is 0, and no operation will happen
            print(f"Invalid Input, {target.name} has made you paid your mistake") # lets now the user the incorrect input and user pays the penalty


class Enemies(Fighter):  
    def __init__(self, name, attack=5, health=100):  
        super().__init__(name, attack=attack, health=health)
    
    def strike_back(self, target): # same syntax for the def strike function, but used by the villain everytime the villain reacts. Same logic with parameters self and target (hero)
        target.health -= self.attack 
        print(f"{self.name} hits {target.name} for {self.attack} damage. {target.name} has now {target.health} of health")

    
    def is_immune(self, ability_name): # this function connects to the sqlite database and checks if the enemy is immune to the ability being used
        conn = sqlite3.connect("immunity_data.db") # calling on my database created above
        cur = conn.cursor()

        cur.execute(""" 
        SELECT immune_to 
        FROM enemy_immunities 
        WHERE enemy_name = (?) 
        """, (self.name,)) # query to retrieve the ability the enemy is immune 

        result = cur.fetchone() # obtain the result from the query
        conn.close() 

        if result: 
            return result[0] == ability_name # check if the result matches the current ability being used
        return False # if no result is found, assumes the enemy is not immune
    

class GameManager:
# this class is where the crunching takes place and executes the game. 
    def __init__(self): # getting started and laying out the heroes, villains, worlds and the selection to begin the game
        self.heroes = ["Crash Bandicoot", "Sonic", "Mario", "Cup Head", "Mega Man", "Pepsi Man"]
        self.villains = ["Xerxes", "Scipio", "Nero", "The Comedian", "Hannibal", "Red Skull", "Jack the Ripper", "Ozymandias", "Thanos", "Caligula"]
        self.worlds = ["The Pits", "Living Forest", "N. Sanity Beach", "Raccoon City", "Sentinel Island", "Death Valley", "Arkham Asylum", "Babylon", "Omaha Beach", "Carthage"]
        print("Welcome to FightPlomacy: Where Diplomacy is overrated. So is mercy")
        print("Enter [1] to begin game, [2] for instructions, or [3] to exit")
        try:
            selection = int(input("Enter Number here: ")) # this is where the user will input the next step either calling to start the game, review instructions or exit.
        except ValueError:
            print("Invalid Input")
            return self.__init__()
        if selection == 1: 
            self.start_game() # calls on the hero selection, mode, followed by the main battle function
        elif selection == 2:
            self.game_instructions() # calling on instructions will display instructions, and call back the menu again
        elif selection == 3:
            self.exit_game() # this will exit the game and thank the user for playing

    def start_game(self):
        print("Defeat the villains at all cost!!")
        print("Hero Selection: ")
        for hero in self.heroes: # looping my list of heroes for the user to pick
            print(hero)
        hero_selected = input("Enter Name of Hero: ") # user picks hero by typing the name
        while hero_selected not in self.heroes: # if user types the name incorrectly this while loop will execute until the hero is in the list of heroes
            print("Invalid Hero Selection. Please type the name exactly as shown.")
            hero_selected = input("Enter Name of Hero: ")
        print(f"You have selected: {hero_selected}")
        self.hero = Fighter(hero_selected) # creates my fighter object which represents the hero selected to fight the enemies
        self.game_difficulty() # proceeds to call my next function to select the level of difficulty
    
    def game_difficulty(self):
        print("Enter Difficulty Level [1] for Easy, [2] for Medium, [3] for Difficult: ") # I would rather have the user input integers as references for the difficulty levels
        try:
            difficulty_selection = int(input("Choose your Destiny: ")) # depending on the integer that is input my conditions below create a variable that indicates the number of villains that our hero faces
        except ValueError:
            print("Invalid Input")
            return self.game_difficulty()
        if difficulty_selection == 1:
            villains_to_fight = 5
        elif difficulty_selection == 2:
            villains_to_fight = 8
        elif difficulty_selection == 3:
            villains_to_fight = 10

        print(f"Prepare to fight {villains_to_fight} villains!") 
        self.battle_towers(villains_to_fight) # this moves on to my main battle function, here I am passing the number of villains that the hero will face
    

    def battle_towers(self, villains_to_fight): # this function is taking in the number of villains the hero faces
        selected_villains = random.sample(self.villains, villains_to_fight) # randomize the name of the list of villains, the villains_to_fight is the number of random villain names provided above
        for villain_name in selected_villains: # loops through the selected villain names
            world_name = random.choice(self.worlds) # randomly selecting a world for each fight
            print(f"\nYou are entering {world_name} to fight {villain_name}!")  
            enemy = Enemies(villain_name) # I create my enemy object with the name of the villain

            while self.hero.health > 0 and enemy.health > 0: # as long as the health of the hero and the villain are greater than zero, I will be looping through the sequence below
                print("\nChoose your Move:") # while it loops the user will select the base attack or super attack to hit the villain
                print("[1] Strike (Base attack)")
                print("[2] Power Attack")
                try:
                    move = int(input("Enter Move Number: ")) # user makes selection
                except ValueError:
                    print("Invalid input. Please choose 1 or 2.")
                    continue

                if move == 1:
                    self.hero.strike(enemy)
                elif move == 2:
                    self.hero.use_power_attack(enemy)
                
                if enemy.health <= 0: # once the villain dies the loop will break out and move to the next villain
                    print(f"{enemy.name} has been defeated!")
                    heal_amount = 15 # the hero heals +15 after defeating an enemy
                    self.hero.health += heal_amount 
                    print(f"{self.hero.name} gains {heal_amount} health! Now at {self.hero.health} health.\n") # prints status
                    break
                
            if self.hero.health <= 0: # if the hero dies it calls the exit game function because game is over
                print("You were defeated. Game Over.")
                self.exit_game()
                return # exit the game when hero is defeated
                

        print("Congratulations! You defeated all the villains and won the game!")
        self.exit_game() # exit the game once the hero defeats them all

    
    def game_instructions(self):
        print("Instructions: ")
        print("------------------------------------------------")
        print("FightPlomacy is a turn-based, Mortal Kombat-style tower battle game where players take on the role of heroes battling through villains across worlds!")
        print("Mission Impossible: Defeat All Enemies! ")
        print("Select a Hero from the roster. Available Characters: ")
        for name in self.heroes:
            print(name)
        print("Select a difficulty level: Easy (5 enemies), Medium (8 enemies), or Hard (10 enemies). Travel through random worlds and face random villains")
        print("The heroes and villains starting health is: 100")
        print("Every turn you will get the chance to strike the enemy with your base attack or with a power ability, in return the enemies will always strike you back taking -5 of your health")
        print(f"Hero's base attack: 15. Using power abilities will allow you to defeat the villains faster. These are the available options and the amount of damage: ")
        Power_Abilities().show_abilities()
        print("Hero heals +15 every time an enemy is defeated")
        print("Make sure not to use the same power ability consecutively or be ready to lose -5 health")        
        print("------------------------------------------------")
        self.__init__() # once instructions are printed this goes back to the Game Manager menu.


    def exit_game(self):
        print("Thanks for playing FightPlomacy!")


if __name__ == "__main__":
    GameManager()
