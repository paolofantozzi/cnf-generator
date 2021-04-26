# -*- coding: utf-8 -*-

"""Random generators for cnf pairs."""

from random import choice
from random import randint
from random import seed
from random import shuffle
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from numpy.random import choice as np_choice

from .cnf import CNF
from .cnf import STD_SYMBOLS
from .cnf import Clause
from .cnf import Literal
from .iso_gen import cnf_isomorphic_generator
from .non_iso_gen import cnf_generator_trivial
from .non_iso_gen_paper import non_trivial_non_isomorphic_cnf_generator


def random_cnf(  # noqa: WPS211
    *,
    symbols: List[str] = None,
    min_num_symbols: int = 25,
    max_num_symbols: int = 50,
    min_num_clauses: int = 20,
    max_num_clauses: int = 30,
    avg_literals_per_clause: int = 6,
    all_clauses_same_dimension: bool = True,
    monotone: bool = False,
    random_seed: Optional[int] = None,
    **kwagrs,
) -> CNF:
    """Generate a random cnf based on some parameters."""
    symbols = symbols or list(STD_SYMBOLS)
    symbols = symbols[:]

    if random_seed is not None:
        seed(random_seed)

    num_symbols = randint(min_num_symbols, max_num_symbols)
    shuffle(symbols)
    symbols = symbols[:num_symbols]

    num_clauses = randint(min_num_clauses, max_num_clauses)
    clauses: Set[Clause] = set()
    while len(clauses) < num_clauses:
        this_clause_len = avg_literals_per_clause
        if not all_clauses_same_dimension:
            this_clause_len = randint(1, (avg_literals_per_clause * 2) - 1)

        this_clause_literals: Set[Literal] = set()
        while len(this_clause_literals) < this_clause_len:
            symbol = choice(symbols)
            is_negated = False
            if not monotone:
                is_negated = bool(randint(0, 1))

            literal = Literal(symbol, is_negated)

            this_clause_literals.add(literal)

        clause = Clause(this_clause_literals)
        clauses.add(clause)

    return CNF(clauses)


def random_cnfs(how_many_cnf: int, **kwargs) -> Iterator[CNF]:
    """Return an iterator over many random cnfs."""
    yield from (random_cnf(**kwargs) for _ in range(how_many_cnf))


def random_pairs(
    how_many_pairs,
    *,
    isomorph_probability=0.5,
    non_isomoprh_trivial_probability=0.25,
    non_isomoprh_non_trivial_probability=0.25,
    **kwargs,
) -> Iterator[Tuple[CNF, CNF, int]]:
    """Iterate through pairs of cnfs generated based on the probabilities."""
    # normalize probabilities
    tot_probs = isomorph_probability + non_isomoprh_trivial_probability + non_isomoprh_non_trivial_probability
    isomorph_probability /= tot_probs
    non_isomoprh_trivial_probability /= tot_probs
    non_isomoprh_non_trivial_probability /= tot_probs

    funcs = [
        cnf_isomorphic_generator,
        cnf_generator_trivial,
        non_trivial_non_isomorphic_cnf_generator,
    ]
    funcs_probs = [
        isomorph_probability,
        non_isomoprh_trivial_probability,
        non_isomoprh_non_trivial_probability,
    ]

    for _ in range(how_many_pairs):
        original_cnf = random_cnf(**kwargs)
        func_idx = np_choice(3, p=funcs_probs)
        func_generator = funcs[func_idx]
        new_cnf = func_generator(original_cnf, **kwargs)
        yield original_cnf, new_cnf, func_idx
