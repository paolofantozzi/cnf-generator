# -*- coding: utf-8 -*-

"""Library demo."""

from cnf_generator import random_cnf    # produce una cnf random
from cnf_generator import random_cnfs   # produce n cnf random
from cnf_generator import random_pairs  # produce coppie di cnf

# tutti gli argomenti tranne il numero di formule o di coppie da generare sono opzionali

print(random_cnf(
    symbols=None,  # lista di stringhe corrispondenti ai simboli da utilizzare, se nulla allora [a-zA-Z0-9]+
    min_num_symbols=25,  # quanti simboli differenti utilizzare al minimo per creare la formula
    max_num_symbols=50,  # quanti simboli differenti utilizzare al massimo per creare la formula
    min_num_clauses=20,  # quante clausole minimo deve contenere la formula
    max_num_clauses=30,  # quante clausole massimo deve contenere la formula
    avg_literals_per_clause=6,  # quanti letterali in media per ogni clausola
    all_clauses_same_dimension=True,  # se tutte le clausole devono avere la stessa dimensione (in quel caso la media di prima)
    monotone=False,  # True -> solo letterali positivi
    random_seed=None,  # seed da passare a random se necessario
))

print(random_cnfs(
    3,  # quante cnf generare
    # tutti gli argomenti per la cnf singola opzionali
))

types = ['isomorph', 'trivial non isomorph', 'non trivial non isomorph']

pairs_iterator = random_pairs(
    100,  # quante coppie produrre
    isomorph_probability=0.5,  # probabilità di produrre una coppia di formule isomorfe
    non_isomoprh_trivial_probability=0.25,  # probabilità di produrre una coppia di formule banalmente non isomorfe
    non_isomoprh_non_trivial_probability=0.25,  # probabilità di produrre una coppia di formule non banalmente non isomorfe
    isomorphic_to_result=True,  # questo vale solo nella generazione di coppie non banalmente non isomorfe:
                                # True -> restituisci una formula isomorfa della non isomorfa generata
                                # altrimenti la differenza tra le due formule sarebbe minima e sarebbe facile
                                # confrontare solo la differenza
    # si possono ovviamente passare anche tutti gli argomenti per la generazione della cnf
)
for orig_cnf, new_cnf, pair_type in pairs_iterator:
    print('orig:', orig_cnf)
    print('new:', new_cnf)
    print('type:', types[pair_type])
