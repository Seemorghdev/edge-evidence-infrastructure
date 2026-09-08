from scripts.validate_surfaces import main


def test_all_deployment_surfaces_are_consistent() -> None:
    assert main() == 0
