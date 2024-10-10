from importlib.resources import files

from flow.oddball._utils import list_novel_sounds, parse_trial_list


def test_oddball_files():
    """Test the presence of the oddball files."""
    trials = list()
    for fname in (
        "main1.txt",
        "main2.txt",
        "main3.txt",
        "solo.txt",
        "stp1.txt",
        "stp2.txt",
        "stp3.txt",
    ):
        trials.extend(parse_trial_list(files("flow.oddball") / "trialList" / fname))
    trials = list(set([trial[1] for trial in trials if trial[1].startswith("wav")]))
    novel_sounds = [sound.split("-")[0] for sound in list_novel_sounds()]
    trials = sorted(trials)
    novel_sounds = sorted(novel_sounds)
    assert sorted(trials) == sorted(novel_sounds)
