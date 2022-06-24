import os
import matplotlib.pyplot as plt
import time
import numpy
import random
# from numpy import mean


# from tabulate import tabulate


class Game:


    def __init__(self, levels):
        # Get a list of strings as levels
        # Store level length to determine if a sequence of action passes all the steps
        self.levels = levels
        self.current_level_index = -1
        self.current_level = ""

        self.winers_path = set()
        self.history = {}
        self.generation_number = 0
        self.population = dict()
        self.avearge = 0
        # if next generation wasnt good enough
        self.previous_generation = dict()
        self.bad_generation = False 

        self.stop = False


    def load_next_level(self):
        self.current_level_index += 1
        self.current_level = self.levels[self.current_level_index]
        print("===========================================")
        print("⏳ CURRENT_LEVEL:{}".format(self.current_level))
        print("===========================================")

        self.generation_number = 0
        self.population = dict()
        self.average = 0
        self.previous_generation = dict()
        self.bad_generation = False
        self.stop = False


    def generate_random_path(self, number):
        for c in range(number):
            # generate a string like 0002011001..
            chromosome = "".join([str(random.randint(0,2)) for i in range(len(self.current_level))])
            self.population[chromosome] = sum(self.get_score(chromosome))
        self.average = self.average_of_population(self.population)
        # print(self.chromosome_score)


    def get_score(self, actions):
        # Get an action sequence and determine the steps taken/score
        # Return a tuple, the first one indicates if these actions result in victory
        # and the second one shows the steps taken
        current_level = self.current_level
        # add flag to the level
        current_level = current_level + "F"
        # shift each step to left
        # each action means changed to mario state -> 0:stand, 1:jumb, 2:down 
        actions = "0" + actions

        # print(current_level)
        # print(actions)
        
        win = False
        win_score = 0

        best_score = [0]
        # detail of scores
        flag_score = 0
        steps_score = 0
        gomba_score = 0
        lakipo_score = 0
        mushroom_score = 0

        # O:Mario, []:unit of ground, ^:jump, >>>:move to left
        # *:enemy, +:muchroom, |>: flag
        for i in range(len(current_level)):
            current_step = current_level[i]
            
            if (current_step == '_'):
                #-------------
                #     *
                # >>> ^O   
                #[ ] [ ] [ ]
                #-------------
                if current_level[i-1] == "L" and actions[i-1]=="2" and actions[i]=="1":
                    steps_score += 1
                    lakipo_score += 2
                #-------------
                #
                # O > 
                #[ ] [ ] [ ]
                #-------------
                else:
                    steps_score += 1


            elif current_step == 'G':
                #-------------
                #  >>>>>> O
                # ^   *
                #[ ] [ ] [ ]
                #-------------
                if (actions[i] == '1'):
                    steps_score += 1
                #-------------
                #     >>> O
                #     ^   *
                #[ ] [ ] [ ]
                #-------------
                elif (actions[i-1] == '1'):
                    steps_score += 1
                    gomba_score += 2
                else:
                    # lose
                    total_score = [steps_score, gomba_score, lakipo_score, mushroom_score]
                    if sum(total_score) >= sum(best_score):
                        best_score = total_score
                        steps_score = gomba_score = lakipo_score = mushroom_score = 0


            elif current_step == 'L':
                #-------------
                #     *
                #     >>> 0      
                #[ ] [ ] [ ]
                #-------------
                if (actions[i] == '2') and (actions[i-1]!='1'):
                    steps_score += 1
                else:
                    # lose
                    total_score = [steps_score, gomba_score, lakipo_score, mushroom_score]
                    if sum(total_score) >= sum(best_score):
                        best_score = total_score
                        steps_score = gomba_score = lakipo_score = mushroom_score = 0
                    

            elif current_step == 'M':
                #-------------
                #  >>>>>> 0
                # ^   +
                #[ ] [ ] [ ]
                #-------------
                if (actions[i] == '1'):
                    steps_score += 1
                #-------------
                #     
                # >>> +O   
                #[ ] [ ] [ ]
                #-------------
                else:
                    steps_score += 1
                    mushroom_score += 2


            elif current_step == 'F':
                if steps_score == len(current_level)-1:
                    win = True
                    win_score += 5
                #-------------
                #         O
                #         |>
                #[ ] [ ] [ ]
                #-------------
                if (actions[i] == '1'):
                    flag_score += 1

            
            else:
                # something wrong with this level
                break
              


        if win == True:
            best_score = [win_score, flag_score, steps_score, gomba_score, lakipo_score, mushroom_score]
            self.winers_path.add((actions[1:],sum(best_score)))

        else:
            total_score = [ 0 ,flag_score, steps_score, gomba_score, lakipo_score, mushroom_score]       

            if sum(total_score) >= sum(best_score):
                best_score = total_score
            else:
                best_score = [0, flag_score] + best_score
                
                    
        # print("best_score:{}\nwin_score:{}\nsteps_score:{}\nflag_score:{}".format(best_score,win_score,steps_score,flag_score))
        # print("gomba_score:{}\nlakipo_score:{}\nmushroom_score:{}".format(gomba_score,lakipo_score,mushroom_score))

        return best_score


    def preferable_paths(self):
        sorted_population = sorted(self.population.items(), key=lambda item: item[1], reverse=True)
        prefections = dict(sorted_population[:int(len(self.population)/2)])
        return prefections


    def crossover(self, parent_1, parent_2):
        p1 = [p for p in parent_1[0]]
        p2 = [p for p in parent_2[0]]

        # print("parent_1:{}, parent_2:{}".format(parent_1,parent_2))
        start_section_size = random.randint(1,len(parent_1[0])-2)
        end_section_size = random.randint(start_section_size+1,len(parent_2[0]))
        
        temp = p1[start_section_size:end_section_size]
        p1[start_section_size:end_section_size] = p2[start_section_size:end_section_size]
        p2[start_section_size:end_section_size] = temp

        child_1 = ("".join(p1),sum(self.get_score("".join(p1))) )
        child_2 = ("".join(p2),sum(self.get_score("".join(p2))) )

        # print("child_1 :{}, child_2 :{}".format(child_1,child_2))
        # print("-----------------------------------------")

        return [child_1, child_2]


    def create_next_generation(self, number_of_genration):
        self.average = self.average_of_population(self.population)
        self.history[self.current_level_index] = [(self.average, self.population)]
        
        while (self.generation_number < number_of_genration) and self.stop!=True:
            self.generation_number += 1
            self.previous_generation = self.population
            self.population = self.preferable_paths()
            
            # shuffle the the bests of previous generation
            if self.bad_generation == True:
                temp = list(self.population.items())
                random.shuffle(temp)
                self.population = dict(temp)
                bad_generation = False

            # print("preferable_paths:\n{}".format(self.population))
            nxt = 0
            done = False
            next_generation = list()

            for i in list(self.population.items())[:-1]:
                if done == True:
                    break
                nxt += 1
                next_generation = list(set(next_generation))
                for j in list(self.population.items())[nxt:]:
                    if len(next_generation) == len(self.previous_generation):
                        done = True
                        break
                    next_generation = next_generation + self.crossover(i,j)
                    # print(i,j,nxt,next_generation)

            # print(next_generation)
            self.population = dict(next_generation[:len(self.previous_generation)])
            self.mutation()
            self.average = self.average_of_population(self.population)

            # print("gnn:",self.generation_number)
            # print("avr:",self.avearge)
            # print("prv:",self.previous_generation)
            # print("nxt:",self.population)

            self.history[self.current_level_index].append((self.average, self.population))

            if sum(list(self.population.values())) < sum(list(self.previous_generation.values())) \
            or len(self.previous_generation)!=len(self.population):
                # print("========== ⚠️  BAD GENERATION ⚠️  ==========")
                self.population = self.previous_generation
                self.bad_generation = True
            
            # print("-------------------------------------------")
        
            self.stop = self.stop_creating(number_of_genration)
        
        return self.population


    def average_of_population(self, pop):
        score_list = [int(i) for i in pop.values()]
        avr = round(numpy.mean(score_list),2)
        return avr


    def stop_creating(self,num_of_gen):
        if (self.generation_number < num_of_gen):
            for p in self.population.values():
                if (abs(int(p)-self.avearge)> 0.1) : 
                    return False

        print("🔻 LEVEL: {}".format(self.current_level))
        print("\n🔻 BEST GENERATIONS IN [{}] GENERATIONS: {}".format(self.generation_number,self.population))
        print("\n🔻 CONVERGENCE SCORE OF THE BEST GENERATION IS: {}".format(self.avearge))
        print("___________________________________________")

        return True


    def mutation(self):
        # choice chromosome
        ch = random.choice(list(self.population.items()))[0]
        genes = [x for x in ch]
        # calculate for probability of each genes
        prob_x = 1/((genes.count('0')*1) + (genes.count('1')*5) + (genes.count('2')*2))
        prob_char = {'0':prob_x, '1':5*prob_x, '2':2*prob_x}
        probability = [prob_char[g] for g in genes]
        
        # choose random genes with them probability
        this_genes = set(random.choices(range(0, len(genes)), tuple(probability), k=random.randint(0,int(len(genes)/2)) ))
        # mutate chosen genes
        for n in this_genes:
            genes[n] = str(random.choices(range(0,3), (0.5, 0.1, 0.2), k=1)[0])
        

    def simulate_this_actions(self,actions):
       
        current_level = self.current_level + "F"
        current_state = [c for c in current_level]
        actions = "0" + actions
        # print(current_state)
        # print(current_level)
        # print(actions)

        os.system('cls' if os.name == 'nt' else 'clear')
        self.graphic(actions,current_state,"","")
        time.sleep(1.5)

        states = {'0':'s', '1':'j', '2':'d'}     
        for i in range(len(actions)):
            os.system('cls' if os.name == 'nt' else 'clear')
            # take an action
            current_action = actions[i]
            # save the element of level
            second_object = current_level[i]
            current_state[i] = "P"
            current_state = self.graphic(actions, current_state,states[current_action],second_object)
            # current_state[i] = second_object
            time.sleep(0.5)


    def graphic(self,actions,current_state,mario_state,second_object):

        emoji = {"🍄","🕹","🧱","🚩","🐢","🦔","👾","💀","😝","😎","🙄","🙃","🤩","😊"}

        counter = 0
        sky = ""
        ground = ""
        base = "".join(["x".join("🧱 ") for i in range(len(current_state))])

        for element in current_state:
            if (element == "L"):
                sky = sky + "🐢 "
                ground = ground + "   "
            elif (element == "M"):
                ground = ground + "🍄 "
                sky = sky + "   "
            elif (element == "G"):
                ground = ground + "👾 "
                sky = sky + "   "
            
            elif (element == "P"):
                #stand
                current_state[counter] = second_object 
                
                if mario_state == 's':
                    if second_object == "G":
                        if actions[counter-1]=='1':
                            sky = sky + "   "
                            ground = ground + "😝 "
                            current_state[counter] = "_" 
                        else:
                            sky = sky + "   "
                            ground = ground + "💀 "       
                    elif second_object == "M":
                        sky = sky + "   "
                        ground = ground + "🤩 "
                        current_state[counter] = "_"
                    elif second_object == "L":
                        sky = sky + "🐢 "
                        ground = ground + "💀 "
                    elif second_object == "F":
                        sky = sky + "   "
                        ground = ground + "😎 "
                    else:
                        sky = sky + "   "
                        ground = ground + "😊 "
                    
                # jump
                elif mario_state == 'j':
                    if second_object == "G":
                        sky = sky + "😱 "
                        ground = ground + "👾 "
                    elif second_object == "M":
                        sky = sky + "🥺 "
                        ground = ground + "🍄 "
                    elif second_object == "L":
                        sky = sky + "💀 "
                        ground = ground + "   "
                    elif second_object == "F":
                        sky = sky + "😎 "
                        ground = ground + "🚩 "
                    else:
                        if (current_state[counter-1] == "L") and (actions[counter-1]=='2'):
                            sky = sky[:-3] + "   " + "😆 "
                            ground = ground + "   "
                            current_state[counter-1] = "_"
                        else:
                            sky = sky + "🙂 "
                            ground = ground + "   "
                # down
                elif mario_state =='d':
                    if second_object == "G":
                        if actions[counter-1] == '1':
                            sky = sky + "   "
                            ground = ground + "😝 "
                            current_state[counter] = "_"
                        else:
                            sky = sky + "   "
                            ground = ground + "💀 "
                    elif second_object == "M":
                        sky = sky + "   "
                        ground = ground + "🤩 "
                        current_state[counter] = "_"
                    elif second_object == "L":
                        sky = sky + "🐢 "
                        ground = ground + "🙄 "
                    elif second_object == "F":
                        sky = sky + "   "
                        ground = ground + "😎🚩"
                    else:
                        sky = sky + "   "
                        ground = ground + "😖 "
            else:
                if counter == len(current_state)-1:
                    sky = sky + "   "
                    ground = ground + " 🚩"
                else:
                    sky = sky + "   "
                    ground = ground + "   "

            counter += 1
        print("\n=========================================")
        print("🗺️  CURRENT_LEVEL  : {}".format(self.current_level))
        print("🎮 CURRENT_ACTIONS: {}".format(actions[1:]))
        # [steps_score, flag_score, gomba_score, lakipo_score, mushroom_score]  
        score_list = self.get_score("".join(actions[1:]))

        print("\n⭐ MUX SCORE:{}".format(sum(score_list)))
        print("\n🏆: {}|🚩: {}|🧱: {}|👾: {}|🐢: {}|🍄: {}|".\
            format(score_list[0],score_list[1],score_list[2],score_list[3],score_list[4],score_list[5]))
        print("=========================================")
        print(sky+"\n"+ground+"\n"+base )
        print("=========================================")

        return current_state


    def draw_plot(self):
    # { ln1:[ (av:{}),(),(), ... ], ln2: ... }
       
        generations_history = self.history[self.current_level_index]
        generations_average = [gh[0] for gh in generations_history]

        win_generation_num = int()
        threshold = 0
        counter = 1

        # gn = (avr,{ch:scr, ... })
        for gn in generations_history:
            print("\nFOR THIS LEVEL: [{}] {}".format(self.current_level_index,self.current_level))
            print("-------------------------------------------")
            gn_index = generations_history.index(gn)
            print("🔹 GENERATION NUMBER[{}]".format(counter))

            data = list(gn[1].items())
            check_for_win = [act in g.winers_path for act in data] 
            # if all each string is a winner path
            if False not in check_for_win:
                threshold = gn[0]
                win_generation_num = counter

            answer = input("📈 DIAGRAM?[Y/N]: ")
            if answer == "y":    
                plt.title("Generation [{}]".format(counter))
                plt.xlabel(" Chromosomes ")
                plt.ylabel(" Scores ")
                plt.plot(range(1,len(gn[1].keys())+1),gn[1].values() , 'ro')
                plt.show()
            counter += 1
            os.system('cls' if os.name == 'nt' else 'clear')

        print("___________________________________________")



        print("\nFOR THIS LEVEL: [{}] {}".format(self.current_level_index,self.current_level))
        print("-------------------------------------------")
        if threshold != 0:
            print("🏆 AFTHER [{}]TH GENERATION PATHS ARE WINNING THE GAME.".format(win_generation_num))
            answer = input("📊 DIAGRAM?[Y/N]: ")
            if answer == "y":
                plt.title("Level [{}] Generations".format(self.current_level))
                plt.xlabel("Chromosomes")
                plt.ylabel("Avearge Scores")
                plt.plot(range(len(generations_history)), generations_average, 'ro')
                plt.axhline(y=threshold, color='b', linestyle='-')
                plt.show()
        else:
            print("💀 NON OF GENERATIONS COULD WIN THE GAME.")
            print("-------------------------------------------")
        print("===========================================")
        os.system('cls' if os.name == 'nt' else 'clear')



#---------------------------------------------------------
# END OF CLASS
#---------------------------------------------------------



if __name__ == "__main__":

    # draw_plot()


    stop = False
    # levels = ["__M_____",
    #           "____G_____",
    #           "__G___L_",
    #           "__G__G_L___",
    #           "____G_ML__G_",
    #           "____G_MLGL_G_",
    #           "_M_M_GM___LL__G__L__G_M__",
    #           "____G_G_MMM___L__L_G_____G___M_L__G__L_GM____L____",
    #           "___M____MGM________M_M______M____L___G____M____L__G__GM__L____ML__G___G___L___G__G___M__L___G____M__",
    #           "_G___M_____LL_____G__G______L_____G____MM___G_G____LML____G___L____LMG___G___GML______G____L___MG___"]
    levels =["____G_MLGL_G_"]

    g = Game(levels)

    for lv in g.levels:
        print("\n============ NEXT LEVEL LOADED ============")
        g.load_next_level()
        g.generate_random_path(200);
        g.create_next_generation(10)
        # g.simulate_this_actions("")
        print("\n🍿  SIMULATION ON THE BEST POPULATION STARTED.")
        count = 0
        for ch in g.population.keys():
            print("___________________________________________\n")
            print("[{}] ACTION STRING RAMAIND | A{}: {}".format(len(g.population)-count,count,ch))
            print("-------------------------------------------")
            answer = input("▶️   COUNTINIU?[Y/N]: ")

            if answer == "y":
                g.simulate_this_actions(ch)
            elif answer == "stop":
                print("\n___________________________________________")
                print("\n🎬 GAME STOPED")
                stop = True
                break
            else:
                count = 0
                print("___________________________________________")
                time.sleep(0.5)
                break
            count += 1
        if stop == True:
            break 
        g.draw_plot()