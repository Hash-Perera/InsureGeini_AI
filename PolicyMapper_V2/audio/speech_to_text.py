import whisper

model = whisper.load_model("base")

insurance_jargon = [
    "accident", "adjuster", "airbag", "appraisal", "assessment", "auto claim",
    "automobile", "authorized repair", "beneficiary", "body shop", "bumper",
    "car insurance", "car policy", "car rental", "carrier", "claim number",
    "claim process", "collision", "comprehensive coverage", "compensation",
    "covered loss", "crash", "damage assessment", "deductible", "depreciation",
    "driver", "estimate", "excess", "exclusions", "fault determination",
    "fender bender", "file a claim", "fire damage", "garage", "glass repair",
    "incident report", "indemnity", "inspection", "insured party",
    "insurance adjuster", "insurance claim", "insurance coverage",
    "insurance policy", "liability", "liability coverage", "limit of liability",
    "loss adjuster", "loss of use", "mechanical failure", "motor vehicle report",
    "negligence", "no-fault insurance", "non-collision damage", "not-at-fault",
    "notification of loss", "policyholder", "police report", "pre-accident condition",
    "premium", "property damage", "reimbursement", "repair estimate",
    "replacement cost", "rental coverage", "reporting officer", "residual damage",
    "roadside assistance", "salvage", "settlement", "statement of claim",
    "subrogation", "surcharge", "third-party liability", "theft", "total loss",
    "towing", "traffic collision", "underinsured motorist", "uninsured motorist",
    "vehicle damage", "vehicle identification number", "vehicle inspection",
    "windshield damage", "witness statement", "wreck", "write-off"
]

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path, language="en", initial_prompt=insurance_jargon.join(", "))
    return result["text"]
