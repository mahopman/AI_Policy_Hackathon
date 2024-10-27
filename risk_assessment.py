class RiskAssessment(dict):
    RISK_LEVELS = {
        "low": 0.33,
        "medium": 0.66,
        "high": 1.0
    }

    def __init__(self, risk_level, **kwargs):
        super().__init__()
        self['risk_level'] = self.convert_risk_level(risk_level)
        for key, value in kwargs.items():
            self[key] = value

    def __repr__(self):
        return (f"RiskAssessment({', '.join([f'{key}={value!r}' for key, value in self.items()])})")

    def convert_risk_level(self, risk_level):
        return self.RISK_LEVELS.get(risk_level.lower(), 0)