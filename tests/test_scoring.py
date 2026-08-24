def test_score_bounds_formula():
    multiple = 10.0
    velocity_ratio = 4.0
    engagement = 0.2
    outlier_component = min(multiple / 5.0, 1.0) * 50
    velocity_component = min(velocity_ratio, 3.0) / 3.0 * 30
    engagement_component = min(engagement / 0.08, 1.0) * 20
    score = outlier_component + velocity_component + engagement_component
    assert 0 <= score <= 100
    assert score == 100
