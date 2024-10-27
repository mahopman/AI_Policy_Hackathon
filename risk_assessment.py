class RiskAssessment:
    RISK_LEVELS = {
        "low": 0.33,
        "medium": 0.66,
        "high": 1.0
    }

    def __init__(self, victim, violence_type, reality, risk_level):
        self.victim = victim
        self.violence_type = violence_type
        self.reality = reality
        self.risk_level = self.convert_risk_level(risk_level)

    def __repr__(self):
        return (f"RiskAssessment(victim='{self.victim}', "
                f"violence_type='{self.violence_type}', "
                f"reality='{self.reality}', "
                f"risk_level='{self.risk_level}')")
    
    def convert_risk_level(self, risk_level):
        return self.RISK_LEVELS.get(risk_level.lower(), 0)
    