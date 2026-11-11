from copy import deepcopy
from decimal import Decimal

import pytest

from scoreboard.knight_reports import METRICS, combine_captures, parse_capture, parse_dollars
from scoreboard.knight_export import read_export, verify_displayed_2019
from scoreboard.download import ROOT


def capture():
    return dict(schools=['A', 'B'], metrics=list(METRICS), tables=[
        dict(years=['2018', '2019'], values=[['$0.00', '$1,234.56'], ['N/A', '$2.00']])
        for _ in METRICS])


def test_missing_zero_and_cents_remain_distinct():
    assert parse_dollars('N/A') is None
    assert parse_dollars('$0.00') == Decimal('0')
    assert parse_dollars('$1,234.56') == Decimal('1234.56')
    frame = parse_capture(capture(), 'https://example.com/report')
    assert len(frame) == 32
    assert frame.reported.sum() == 24
    with pytest.raises(ValueError, match='Unrecognized'):
        parse_dollars('2019 $1,000.00')


def test_report_shape_and_order_are_checked():
    data = capture()
    data['tables'][1]['years'].reverse()
    with pytest.raises(ValueError, match='Misaligned'):
        parse_capture(data, 'source')
    data = capture()
    data['tables'][0]['values'][0].pop()
    with pytest.raises(ValueError, match='align'):
        parse_capture(data, 'source')


def test_overlapping_batches_require_identical_values():
    first = parse_capture(capture(), 'first')
    assert len(combine_captures([first, first])) == len(first)
    changed = deepcopy(capture())
    changed['tables'][0]['values'][0][0] = '$7.00'
    with pytest.raises(ValueError, match='Conflicting'):
        combine_captures([first, parse_capture(changed, 'second')])


def test_html_error_cannot_be_imported_as_excel(tmp_path):
    path = tmp_path / 'download.xlsx'
    path.write_text('<html><title>Page not found</title></html>')
    with pytest.raises(ValueError, match='real XLSX'):
        read_export(path)


@pytest.mark.skipif(not (ROOT/'data/private/knight_reports/knight_2010_2019_30e5ca83.xlsx').exists(),
                    reason='Registered financial workbook is not redistributed')
def test_acquired_workbook_and_independent_report_agree():
    panel, _ = read_export(ROOT/'data/private/knight_reports/knight_2010_2019_30e5ca83.xlsx')
    assert len(panel) == 2400
    assert panel.unitid.nunique() == 240
    assert panel.total_expenses.notna().sum() == 2289
    assert panel[list(METRICS)].notna().any(axis=1).sum() == 2291
    capture_path = ROOT/'data/private/knight_reports/dda3742f.displayed.json'
    if capture_path.exists():
        assert verify_displayed_2019(panel, capture_path) == 1920
