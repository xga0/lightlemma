"""
Tests for the Porter Stemmer implementation.
"""
import pytest
from lightlemma.stemmer import stem

def test_empty_input():
    assert stem("") == ""
    with pytest.raises(TypeError):
        stem(None)
    with pytest.raises(TypeError):
        stem(123)
    with pytest.raises(TypeError):
        stem(["word"])

def test_short_words():
    assert stem("a") == "a"
    assert stem("be") == "be"
    assert stem("the") == "the"
    assert stem("at") == "at"
    assert stem("in") == "in"
    assert stem("on") == "on"

def test_step1a():
    # SSES -> SS
    assert stem("caresses") == "caress"
    assert stem("ponies") == "poni"
    assert stem("ties") == "ti"
    assert stem("caress") == "caress"
    assert stem("cats") == "cat"

def test_step1b():
    # (m>0) EED -> EE
    assert stem("agreed") == "agree"
    assert stem("feed") == "feed"
    
    # (*v*) ED ->
    assert stem("plastered") == "plaster"
    assert stem("bled") == "bled"
    assert stem("motored") == "motor"
    
    # (*v*) ING ->
    assert stem("motoring") == "motor"
    assert stem("sing") == "sing"
    assert stem("walking") == "walk"

def test_step1c():
    # (*v*) Y -> I
    assert stem("happy") == "happi"
    assert stem("sky") == "sky"

def test_step2():
    assert stem("relational") == "relat"
    assert stem("conditional") == "condit"
    assert stem("rational") == "ration"
    assert stem("valenci") == "valenc"
    assert stem("hesitanci") == "hesit"
    assert stem("digitizer") == "digit"
    assert stem("conformabli") == "conform"
    assert stem("radicalli") == "radic"
    assert stem("differentli") == "differ"
    assert stem("vileli") == "vile"
    assert stem("analogousli") == "analog"
    assert stem("vietnamization") == "vietnam"
    assert stem("predication") == "predic"
    assert stem("operator") == "oper"
    assert stem("feudalism") == "feudal"
    assert stem("decisiveness") == "decis"
    assert stem("hopefulness") == "hope"
    assert stem("callousness") == "callous"
    assert stem("formaliti") == "formal"
    assert stem("sensitiviti") == "sensit"
    assert stem("sensibiliti") == "sensibl"

def test_step3():
    assert stem("triplicate") == "triplic"
    assert stem("formative") == "form"
    assert stem("formalize") == "formal"
    assert stem("electriciti") == "electric"
    assert stem("electrical") == "electric"
    assert stem("hopeful") == "hope"
    assert stem("goodness") == "good"

def test_step4():
    assert stem("revival") == "reviv"
    assert stem("allowance") == "allow"
    assert stem("inference") == "infer"
    assert stem("airliner") == "airlin"
    assert stem("gyroscopic") == "gyroscop"
    assert stem("adjustable") == "adjust"
    assert stem("defensible") == "defens"
    assert stem("irritant") == "irrit"
    assert stem("replacement") == "replac"
    assert stem("adjustment") == "adjust"
    assert stem("dependent") == "depend"
    assert stem("adoption") == "adopt"
    assert stem("homologou") == "homolog"
    assert stem("communism") == "commun"
    assert stem("activate") == "activ"
    assert stem("angulariti") == "angular"
    assert stem("homologous") == "homolog"
    assert stem("effective") == "effect"
    assert stem("bowdlerize") == "bowdler"

def test_step5a():
    assert stem("probate") == "probat"
    assert stem("rate") == "rate"
    assert stem("cease") == "ceas"

def test_step5b():
    assert stem("controll") == "control"
    assert stem("roll") == "roll"

def test_real_words():
    assert stem("sitting") == "sit"
    assert stem("running") == "run"
    assert stem("goes") == "goe"
    assert stem("flying") == "fli"
    assert stem("happiness") == "happi"
    assert stem("beautiful") == "beauti"
    assert stem("intelligence") == "intellig"
    assert stem("computational") == "comput"
    assert stem("engineering") == "engineer"
    assert stem("scientific") == "scientif"
    assert stem("mathematics") == "mathemat"
    assert stem("physics") == "physic"
    assert stem("chemistry") == "chemistri"
    assert stem("biology") == "biolog"
    assert stem("psychology") == "psycholog"
    assert stem("computer") == "comput"
    assert stem("science") == "scienc"
    assert stem("artificial") == "artifici"
    assert stem("machine") == "machin"
    assert stem("learning") == "learn"

def test_special_cases():
    # Words that should not be stemmed
    assert stem("news") == "news"
    assert stem("proceed") == "proceed"
    assert stem("exceed") == "exceed"
    assert stem("succeed") == "succeed"
    
    # Special verb forms
    assert stem("doing") == "do"
    assert stem("going") == "go"
    assert stem("being") == "be"
    
    # Y/IE transformations
    assert stem("lying") == "lie"
    assert stem("dying") == "die"
    assert stem("tying") == "tie"

def test_compound_words():
    assert stem("grandmother") == "grandmoth"
    assert stem("underground") == "underground"
    assert stem("overwhelming") == "overwhelm"
    assert stem("underneath") == "underneath"
    assert stem("understanding") == "understand"
    assert stem("waterproof") == "waterproof"

def test_contractions():
    assert stem("isn't") == "isn't"
    assert stem("don't") == "don't"
    assert stem("won't") == "won't"
    assert stem("they're") == "they'r"
    assert stem("we've") == "we'v"

def test_capitalization():
    assert stem("RUNNING") == "run"
    assert stem("Running") == "run"
    assert stem("rUnNiNg") == "run"
    assert stem("HAPPINESS") == "happi"
    assert stem("Happiness") == "happi"

def test_repeated_application():
    # Test that stemming is idempotent
    word = "running"
    first_stem = stem(word)
    second_stem = stem(first_stem)
    assert first_stem == second_stem

def test_whitespace_handling():
    assert stem("  running  ") == "run"
    assert stem("\trunning\n") == "run"
    assert stem(" ") == ""
    assert stem("\t\n") == "" 