from src.connective_waxaa_focus import analyze_connective_waxaa_focus


def test_snu_holdout_sentence_initial_wuxuuna_is_recognized():
    sentence = (
        "Wuxuuna u balan qaaday in ay inta awoda Jaamacadda ah laga caawin doono."
    )
    result = analyze_connective_waxaa_focus(sentence)

    assert result.recognized is True
    assert result.particle == "Wuxuuna"
    assert result.boundary == "input_start"
    assert result.subject_clitic == "uu"
    assert result.subject_persons == ("3sg_m",)


def test_bible_holdout_sentence_initial_wuxuuna_independently_corrobates_distribution():
    sentence = "Wuxuuna iyaga ku yidhi, Miyaydnaan masaalkan garanaynin?"
    result = analyze_connective_waxaa_focus(sentence)

    assert result.recognized is True
    assert result.particle == "Wuxuuna"
    assert result.boundary == "input_start"
    assert result.subject_clitic == "uu"
    assert result.subject_persons == ("3sg_m",)


def test_villa_somalia_sentence_initial_waxaadna_is_positive_control():
    sentence = (
        "Waxaadna ogaataan in dib u eegis lagu samaynayo Xeerka Ciqaabta ee soo "
        "baxay sannadkii 1964-tii, si loo xaqiijiyo inaan loo adeegsan weriye kasta."
    )
    result = analyze_connective_waxaa_focus(sentence)

    assert result.recognized is True
    assert result.particle == "Waxaadna"
    assert result.boundary == "input_start"
    assert result.subject_clitic == "aad"
    assert result.subject_persons == ("2sg", "2pl")


def test_attested_separated_waxa_ayna_is_not_silently_promoted_to_exact_waxayna():
    sentence = (
        "Iyadoo laga ambaqaadayo go’aankii Ra’iisul Wasaaraha XFS ee ahaa in cid kasta "
        "ay ka qayb qaadato Dagaalka lagu ciribtirayo Khawaarijta ayay Wasaaradda "
        "Tamarta iyo Kheyradka Biyaha isugu yimaadeen kulankan waxa ayna ballanqaadeen "
        "in taageero hiil iyo hooba ay la garab taaganyihiin Ciidanka Qaranka."
    )
    result = analyze_connective_waxaa_focus(sentence)

    assert result.recognized is False
