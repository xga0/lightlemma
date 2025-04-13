"""
Tests for the lemmatizer module.
"""
import pytest
from lightlemma import lemmatize

def test_empty_input():
    assert lemmatize("") == ""
    assert lemmatize(None) == None

def test_irregular_verbs():
    assert lemmatize("am") == "be"
    assert lemmatize("is") == "be"
    assert lemmatize("are") == "be"
    assert lemmatize("was") == "be"
    assert lemmatize("were") == "be"
    assert lemmatize("been") == "be"
    assert lemmatize("being") == "be"
    assert lemmatize("has") == "have"
    assert lemmatize("had") == "have"
    assert lemmatize("having") == "have"
    assert lemmatize("does") == "do"
    assert lemmatize("did") == "do"
    assert lemmatize("done") == "do"
    assert lemmatize("went") == "go"
    assert lemmatize("gone") == "go"
    assert lemmatize("wrote") == "write"
    assert lemmatize("written") == "write"

def test_irregular_adjectives():
    assert lemmatize("better") == "good"
    assert lemmatize("best") == "good"
    assert lemmatize("worse") == "bad"
    assert lemmatize("worst") == "bad"
    assert lemmatize("larger") == "large"
    assert lemmatize("largest") == "large"
    assert lemmatize("heavier") == "heavy"
    assert lemmatize("heaviest") == "heavy"
    assert lemmatize("prettier") == "pretty"
    assert lemmatize("prettiest") == "pretty"

def test_regular_plurals():
    # Basic plurals
    assert lemmatize("cats") == "cat"
    assert lemmatize("boxes") == "box"
    assert lemmatize("studies") == "study"
    assert lemmatize("flies") == "fly"
    assert lemmatize("databases") == "database"
    assert lemmatize("quizzes") == "quiz"
    
    # Special -es cases
    assert lemmatize("addresses") == "address"
    assert lemmatize("watches") == "watch"
    assert lemmatize("wishes") == "wish"
    assert lemmatize("heroes") == "hero"
    
    # Words that should not change
    assert lemmatize("series") == "series"
    assert lemmatize("species") == "species"
    assert lemmatize("boss") == "boss"
    assert lemmatize("status") == "status"
    assert lemmatize("basis") == "basis"

def test_ves_plurals():
    assert lemmatize("leaves") == "leaf"
    assert lemmatize("lives") == "life"
    assert lemmatize("selves") == "self"
    assert lemmatize("wolves") == "wolf"
    assert lemmatize("shelves") == "shelf"
    assert lemmatize("calves") == "calf"
    assert lemmatize("halves") == "half"
    assert lemmatize("knives") == "knife"
    assert lemmatize("wives") == "wife"
    assert lemmatize("thieves") == "thief"
    assert lemmatize("loaves") == "loaf"
    assert lemmatize("hooves") == "hoof"
    assert lemmatize("scarves") == "scarf"
    assert lemmatize("wharves") == "wharf"
    assert lemmatize("elves") == "elf"

def test_latin_plurals():
    # -a endings
    assert lemmatize("phenomena") == "phenomenon"
    assert lemmatize("criteria") == "criterion"
    assert lemmatize("stigmata") == "stigma"
    
    # -i endings
    assert lemmatize("alumni") == "alumnus"
    assert lemmatize("fungi") == "fungus"
    assert lemmatize("cacti") == "cactus"
    assert lemmatize("nuclei") == "nucleus"
    assert lemmatize("radii") == "radius"
    
    # -ae endings
    assert lemmatize("algae") == "alga"
    assert lemmatize("larvae") == "larva"
    assert lemmatize("nebulae") == "nebula"
    
    # -ices endings
    assert lemmatize("indices") == "index"
    assert lemmatize("matrices") == "matrix"
    assert lemmatize("appendices") == "appendix"
    assert lemmatize("vertices") == "vertex"
    
    # Other Latin forms
    assert lemmatize("data") == "datum"
    assert lemmatize("bacteria") == "bacterium"
    assert lemmatize("memoranda") == "memorandum"
    assert lemmatize("curricula") == "curriculum"
    assert lemmatize("genera") == "genus"
    assert lemmatize("corpora") == "corpus"

def test_irregular_nouns():
    assert lemmatize("children") == "child"
    assert lemmatize("men") == "man"
    assert lemmatize("women") == "woman"
    assert lemmatize("feet") == "foot"
    assert lemmatize("teeth") == "tooth"
    assert lemmatize("geese") == "goose"
    assert lemmatize("mice") == "mouse"
    assert lemmatize("oxen") == "ox"

def test_verb_forms():
    # Past tense
    assert lemmatize("walked") == "walk"
    assert lemmatize("studied") == "study"
    assert lemmatize("tried") == "try"
    assert lemmatize("copied") == "copy"
    assert lemmatize("planned") == "plan"  # Double consonant
    assert lemmatize("agreed") == "agree"  # Keep 'e'
    assert lemmatize("died") == "die"      # Short word
    assert lemmatize("saved") == "save"    # Add 'e'
    
    # Gerund forms
    assert lemmatize("running") == "run"
    assert lemmatize("walking") == "walk"
    assert lemmatize("studying") == "study"
    assert lemmatize("creating") == "create"  # Add 'e'
    assert lemmatize("planning") == "plan"    # Double consonant
    assert lemmatize("seeing") == "see"       # Keep 'ee'
    assert lemmatize("falling") == "fall"     # Keep 'll'
    assert lemmatize("telling") == "tell"     # Keep 'll'
    
    # Other forms
    assert lemmatize("writes") == "write"
    assert lemmatize("takes") == "take"
    assert lemmatize("makes") == "make"
    assert lemmatize("computerize") == "computerize"  # Base form
    assert lemmatize("analyse") == "analyse"         # Base form
    assert lemmatize("simplify") == "simplify"       # Base form
    assert lemmatize("sayeth") == "say"             # Archaic form

def test_adjective_suffixes():
    # -ly endings
    assert lemmatize("quickly") == "quick"
    assert lemmatize("happily") == "happy"
    assert lemmatize("easily") == "easy"
    
    # -ful endings
    assert lemmatize("helpful") == "help"
    assert lemmatize("beautiful") == "beauty"
    
    # -able/-ible endings
    assert lemmatize("readable") == "read"
    assert lemmatize("debatable") == "debate"
    assert lemmatize("likable") == "like"
    assert lemmatize("visible") == "vise"
    
    # -al/-ical endings
    assert lemmatize("logical") == "logic"
    assert lemmatize("historical") == "historic"
    assert lemmatize("musical") == "music"
    
    # -ous/-ious endings
    assert lemmatize("famous") == "famous"
    assert lemmatize("curious") == "curious"
    
    # -ant/-ent endings
    assert lemmatize("dependent") == "depend"
    assert lemmatize("assistant") == "assist"
    
    # Other endings
    assert lemmatize("northward") == "northward"
    assert lemmatize("clockwise") == "clockwise"
    assert lemmatize("uppermost") == "uppermost"

def test_noun_suffixes():
    # -ment endings
    assert lemmatize("government") == "govern"
    assert lemmatize("statement") == "state"
    assert lemmatize("development") == "develop"
    
    # -ness endings
    assert lemmatize("happiness") == "happy"
    assert lemmatize("darkness") == "dark"
    
    # -tion/-sion endings
    assert lemmatize("creation") == "create"
    assert lemmatize("activation") == "activate"
    assert lemmatize("decision") == "decide"
    assert lemmatize("admission") == "admit"
    
    # -ance/-ence endings
    assert lemmatize("acceptance") == "accept"
    assert lemmatize("persistence") == "persist"
    assert lemmatize("performance") == "perform"
    
    # -ity endings
    assert lemmatize("ability") == "able"
    assert lemmatize("visibility") == "visible"
    assert lemmatize("security") == "secure"
    
    # -hood/-ship/-dom endings
    assert lemmatize("childhood") == "child"
    assert lemmatize("friendship") == "friend"
    assert lemmatize("kingdom") == "king"
    
    # -er/-or endings
    assert lemmatize("writer") == "write"
    assert lemmatize("actor") == "act"
    assert lemmatize("teacher") == "teach"
    # Words that should not change
    assert lemmatize("engineer") == "engineer"
    assert lemmatize("soldier") == "soldier"
    
    # -age endings
    assert lemmatize("usage") == "use"
    assert lemmatize("storage") == "store"
    # Words that should not change
    assert lemmatize("age") == "age"
    
    # -ism/-ist endings
    assert lemmatize("socialism") == "socialism"
    assert lemmatize("scientist") == "scientist"
    assert lemmatize("physicist") == "physicist"

def test_case_sensitivity():
    assert lemmatize("Running") == "run"
    assert lemmatize("BOXES") == "box"
    assert lemmatize("Studies") == "study"
    assert lemmatize("CHILDREN") == "child"
    assert lemmatize("Phenomena") == "phenomenon"
    assert lemmatize("LIVES") == "life" 