# -*- coding: utf-8 -*-

"""Implementation of the non isomorphic cnf generation."""

from random import choice
from random import choices
from random import shuffle
from typing import Set

from .cnf import CNF
from .cnf import STD_SYMBOLS
from .cnf import Clause
from .cnf import Literal
from .exceptions import GenerationFailedException
from .exceptions import LiteralNotPossibleToAddException
from .non_iso_gen_paper import non_trivial_non_isomorphic_cnf_generator


def cnf_generator_trivial_add_clause(original_cnf: CNF) -> CNF:
    """Generate a new cnf trivially non isomorph to the original by adding a new clause."""
    literals_set = list(set(original_cnf.literals))

    clauses_length = [len(clause.literals) for clause in original_cnf.clauses]
    new_clause_len = choice(clauses_length)

    # TODO: if the cnf already has all the possible clauses the it will be continue forever
    prev_clauses_len = len(original_cnf.clauses)
    clauses: Set[Clause] = set()
    while prev_clauses_len == len(clauses):
        new_clause_literals = set(choices(literals_set, k=new_clause_len))
        new_clause = Clause(new_clause_literals)
        clauses.add(new_clause)

    return CNF(clauses)


def _add_literal_to_the_first_clause_available(cnf: CNF, literal: Literal) -> CNF:
    """Add literal to the first clause that does not already include it, returning the new cnf."""
    clauses = set(cnf.clauses)
    for clause in clauses:
        literals = set(clause.literals)
        if literal not in literals:
            literals.add(literal)
            clauses = (clauses - {clause}) | {Clause(literals)}
            return CNF(clauses)
    raise LiteralNotPossibleToAddException


def cnf_generator_trivial_add_literal_occurrence(original_cnf: CNF) -> CNF:
    """Generate a new cnf trivially non isomorph to the original by adding a literal coccurrence to a clause."""
    literals_list = list(set(original_cnf.literals))
    shuffle(literals_list)

    for new_literal in literals_list:
        try:
            return _add_literal_to_the_first_clause_available(original_cnf, new_literal)
        except LiteralNotPossibleToAddException:
            pass

    raise GenerationFailedException()


def cnf_generator_trivial_add_new_symbol(original_cnf: CNF) -> CNF:
    """Generate a new cnf trivially non isomorph to the original by adding a new symbol to a clause."""
    symbols = {literal.symbol for literal in original_cnf.literals}
    available_symbols = list(set(STD_SYMBOLS) - symbols)

    new_symbol = choice(available_symbols)
    new_literal = Literal(new_symbol)

    return _add_literal_to_the_first_clause_available(original_cnf, new_literal)


def cnf_generator_trivial(cnf: CNF, **kwargs) -> CNF:
    """Generate a new cnf trivially non isomorph to the original applying a random generator."""
    cnf_gen_func = choice((
        cnf_generator_trivial_add_clause,
        cnf_generator_trivial_add_literal_occurrence,
        cnf_generator_trivial_add_new_symbol,
    ))
    return cnf_gen_func(cnf)


def cnf_generator(cnf: CNF, trivial_non_isomorphism=False) -> CNF:
    """Generate a new cnf non isomorph to the original."""
    if trivial_non_isomorphism:
        return cnf_generator_trivial(cnf)
    return non_trivial_non_isomorphic_cnf_generator(cnf)
