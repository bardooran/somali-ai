from src.predicate_sentence import scan_predicate_agreement


def test_reports_reviewed_masculine_predicate_conflict():
    findings = scan_predicate_agreement("Ninku waa ladan tahay.")
    assert len(findings) == 1
    finding = findings[0]
    assert finding.subject == "Ninku"
    assert finding.copula == "tahay"
    assert finding.expected_copula == "yahay"


def test_reports_reviewed_feminine_predicate_conflict():
    findings = scan_predicate_agreement("Naagtu waa ladan yahay.")
    assert len(findings) == 1
    assert findings[0].expected_copula == "tahay"


def test_matching_reviewed_predicates_are_silent():
    assert scan_predicate_agreement("Ninku waa ladan yahay.") == []
    assert scan_predicate_agreement("Naagtu waa ladan tahay.") == []


def test_unknown_subjects_remain_unjudged():
    assert scan_predicate_agreement("Macallinku waa ladan yahay.") == []
    assert scan_predicate_agreement("Macallinku waa ladan tahay.") == []


def test_scanner_does_not_autocorrect_or_infer_from_suffixes():
    findings = scan_predicate_agreement("Ninku aad buu u ladan yahay.")
    assert findings == []
