class Employee:
    def __init__(self, name, shifts_min, shifts_max, cost_normal, cost_overtime, supervisor=False, custom_rules=None):
        self.name = name
        self.supervisor = supervisor
        self.shifts_min = shifts_min
        self.shifts_max = shifts_max
        self.cost_normal = cost_normal
        self.cost_overtime = cost_overtime
        if custom_rules:
            self.custom_rules = self._get_custom_rules(custom_rules)
        else:
            self.custom_rules = None

    def _get_custom_rules(self, custom_rules):
        rules = []
        for custom_rule in custom_rules:
            rules.append(
                CustomRule(custom_rule)
                )

class CustomRule:
    def __init__(self, custom_rule):
        self.day = custom_rule['day']
        self.shift = custom_rule['shift']

        if custom_rule['rule'] in ["require work", "require free"]:
            self.rule = custom_rule['rule']
        else:
            raise ValueError(f"Unknown custom rule: {custom_rule['rule']}")