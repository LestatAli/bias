class Prompt:
    def __init__(self, choices, correct_index):
        self.choices = choices;
        self.correct_index = correct_index;

class Experiment:
    def __init__(self, version, prompts):
        self.version = version;
        self.prompts = prompts;

ACTIVE_PROMPTS = [
Prompt(["Wrong", "Right"], 1),
Prompt(["Try To Guess", "It's This One"], 1),
Prompt(["Then", "There", "Were Three"], 2),
];

ACTIVE_EXPERIMENT = Experiment(1, ACTIVE_PROMPTS);
