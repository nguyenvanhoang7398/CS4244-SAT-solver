from cdcl_wl import CDCL_WL

from es import einstein

value_list = ["Blend", "Blue Masters", "Dunhill", "Pall Mall", "Prince", 
              "Blue", "Green", "Red", "White", "Yellow",
              "Beer", "Coffee", "Milk", "Tea", "Water",
              "Brit", "Dane", "German", "Norwegian", "Swede",
              "Bird", "Cat", "Dog", "Fish", "Horse"]

def construct_variable(house_id, value):
        return house_id + value_list.index(value) * 5

def gen_einstein():

    def gen_clause1(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Brit"), construct_variable(house_id, "Red")])
            formula.append([construct_variable(house_id, "Brit"), -construct_variable(house_id, "Red")])

    def gen_clause2(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Swede"), construct_variable(house_id, "Dog")])
            formula.append([construct_variable(house_id, "Swede"), -construct_variable(house_id, "Dog")])

    def gen_clause3(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Dane"), construct_variable(house_id, "Tea")])
            formula.append([construct_variable(house_id, "Dane"), -construct_variable(house_id, "Tea")])
        
    def gen_clause4(formula):
        for house_id in range(1, 5):
            formula.append([-construct_variable(house_id, "Green"), construct_variable(house_id+1, "White")])
            formula.append([construct_variable(house_id, "Green"), -construct_variable(house_id+1, "White")])

    def gen_clause5(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Green"), construct_variable(house_id, "Coffee")])
            formula.append([construct_variable(house_id, "Green"), -construct_variable(house_id, "Coffee")])

    def gen_clause6(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Pall Mall"), construct_variable(house_id, "Bird")])
            formula.append([construct_variable(house_id, "Pall Mall"), -construct_variable(house_id, "Bird")])

    def gen_clause7(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Dunhill"), construct_variable(house_id, "Yellow")])
            formula.append([construct_variable(house_id, "Dunhill"), -construct_variable(house_id, "Yellow")])

    def gen_clause8(formula):
        formula.append([construct_variable(3, "Milk")])

    def gen_clause9(formula):
        formula.append([construct_variable(1, "Norwegian")])

    def gen_clause10(formula):
        for house_id in range(2, 5):
            formula.append([-construct_variable(house_id, "Blend"), construct_variable(house_id-1, "Cat"), construct_variable(house_id+1, "Cat")])
            formula.append([-construct_variable(house_id, "Cat"), construct_variable(house_id-1, "Blend"), construct_variable(house_id+1, "Blend")])
        formula.append([-construct_variable(1, "Blend"), construct_variable(2, "Cat")])
        formula.append([-construct_variable(5, "Blend"), construct_variable(4, "Cat")])
        formula.append([-construct_variable(1, "Cat"), construct_variable(2, "Blend")])
        formula.append([-construct_variable(5, "Cat"), construct_variable(4, "Blend")])

    def gen_clause11(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "Blue Masters"), construct_variable(house_id, "Beer")])
            formula.append([construct_variable(house_id, "Blue Masters"), -construct_variable(house_id, "Beer")])

    def gen_clause12(formula):
        for house_id in range(2, 5):
            formula.append([-construct_variable(house_id, "Dunhill"), construct_variable(house_id-1, "Horse"), construct_variable(house_id+1, "Horse")])
            formula.append([-construct_variable(house_id, "Horse"), construct_variable(house_id-1, "Dunhill"), construct_variable(house_id+1, "Dunhill")])
        formula.append([-construct_variable(1, "Dunhill"), construct_variable(2, "Horse")])
        formula.append([-construct_variable(5, "Dunhill"), construct_variable(4, "Horse")])
        formula.append([-construct_variable(1, "Horse"), construct_variable(2, "Dunhill")])
        formula.append([-construct_variable(5, "Horse"), construct_variable(4, "Dunhill")])

    def gen_clause13(formula):
        for house_id in range(1, 6):
            formula.append([-construct_variable(house_id, "German"), construct_variable(house_id, "Prince")])
            formula.append([construct_variable(house_id, "German"), -construct_variable(house_id, "Prince")])

    def gen_clause14(formula):
        for house_id in range(2, 5):
            formula.append([-construct_variable(house_id, "Norwegian"), construct_variable(house_id-1, "Blue"), construct_variable(house_id+1, "Cat")])
            formula.append([-construct_variable(house_id, "Blue"), construct_variable(house_id-1, "Norwegian"), construct_variable(house_id+1, "Blend")])
        formula.append([-construct_variable(1, "Norwegian"), construct_variable(2, "Blue")])
        formula.append([-construct_variable(5, "Norwegian"), construct_variable(4, "Blue")])
        formula.append([-construct_variable(1, "Blue"), construct_variable(2, "Norwegian")])
        formula.append([-construct_variable(5, "Blue"), construct_variable(4, "Norwegian")])

    def gen_clause15(formula):
        for house_id in range(2, 5):
            formula.append([-construct_variable(house_id, "Blend"), construct_variable(house_id-1, "Water"), construct_variable(house_id+1, "Cat")])
            formula.append([-construct_variable(house_id, "Water"), construct_variable(house_id-1, "Blend"), construct_variable(house_id+1, "Blend")])
        formula.append([-construct_variable(1, "Blend"), construct_variable(2, "Water")])
        formula.append([-construct_variable(5, "Blend"), construct_variable(4, "Water")])
        formula.append([-construct_variable(1, "Water"), construct_variable(2, "Blend")])
        formula.append([-construct_variable(5, "Water"), construct_variable(4, "Blend")])

    def gen_constraints(formula):
        gen_atleast1_house_per_val(formula)
        gen_only1_attr_per_house(formula)
        gen_only1_house_per_attr(formula)

    def gen_atleast1_house_per_val(formula):
        for value in value_list:
            atleast1_house = []
            for house_id in range(1, 6):
                atleast1_house.append(construct_variable(house_id, value))
            formula.append(atleast1_house)

    def gen_only1_attr_per_house(formula):
        for house_id in range(1, 6):
            for i in range(len(value_list)):
                start_att_idx = i - i % 5
                for j in range(start_att_idx, i):
                    formula.append([-construct_variable(house_id, value_list[j]), -construct_variable(house_id, value_list[i])])
    
    def gen_only1_house_per_attr(formula):
        for value in value_list:
            for house_id in range(1, 6):
                for j in range(house_id+1, 6):
                    formula.append([-construct_variable(house_id, value), -construct_variable(j, value)])
    
    formula = []
    gen_constraints(formula)
    gen_clause1(formula)
    gen_clause2(formula)
    gen_clause3(formula)
    gen_clause4(formula)
    gen_clause5(formula)
    gen_clause6(formula)
    gen_clause7(formula)
    gen_clause8(formula)
    gen_clause9(formula)
    gen_clause10(formula)
    gen_clause11(formula)
    gen_clause12(formula)
    gen_clause13(formula)
    gen_clause14(formula)
    gen_clause15(formula)
    return formula
if __name__ == "__main__":
    formula = gen_einstein()
    solver = CDCL_WL(formula, [])
    metrics = solver.solve()
    fish_house = 0
    for house_id in range(1, 6):
        if solver.assignments[construct_variable(house_id, "Fish")][0] == 1:
            fish_house = house_id
            print("House {} keeps the fish.".format(house_id))
    owner = ""
    for nationality in ["Brit", "Swede", "Dane", "Norwegian", "German"]:
        if solver.assignments[construct_variable(fish_house, nationality)][0] == 1:
            owner = nationality
    print("The {} keeps the fish.".format(owner)) 