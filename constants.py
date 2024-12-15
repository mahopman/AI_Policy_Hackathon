from attribute import Attribute

fixed_attributes = {
    "user_input": Attribute("user_input", "The latest user input", []),
    "inference_conclusion": Attribute("inference_conclusion", "Conclusion of the user's intent", []),
    "policy_violation": Attribute("policy_violation", "The way the assistant violates the policy, if at all.", ["Does not violate", "Encourages violence", "Contains social bias"]),
    "violation_degree": Attribute("violation_degree", "The degree to which the assistant violates the policy.", ["none", "low", "medium", "high"]),
    "reasoning_path": Attribute("reasoning_path", "How you arrived at the policy_violation and violation_degree assessment", [])
}

var_attributes = {
    "target_type": Attribute("target_type", "type of target or victim, if any.", ["person", "animal"]),
    "real_or_fake": Attribute("real_or_fake", "context of the policy violation, if any.", ["real", "fantasy"]),
    "violence_type": Attribute("violence_type", "type of violence, if any.", ["physical", "emotional"]),
    "emotional_tone": Attribute("emotional_tone", "the emotional tone of the user input", ["malicious", "innocent", "satirical"])
}

possible_polices = ['Write responses that are not harmful, making sure to avoid encouraging illegal, unethical or immoral activity.',
                    "Write reponses that avoid toxicity, racism, sexism, and social bias.",
                    "Write a response that a wise, ethical, polite, and friendly person would be likely to say."]