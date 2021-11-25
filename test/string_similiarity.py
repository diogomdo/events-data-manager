import difflib

# sim = difflib.SequenceMatcher(None, "Leipzig", "Lokomotive Leipzing (Ger)").ratio()
# sim = difflib.SequenceMatcher(None, "Leipzig", "Hildesheim (Ger)").ratio()
# sim = difflib.SequenceMatcher(None, "'FK Futebol Trinec'", "Trinec").ratio()
sim = difflib.SequenceMatcher(None, "Vfv Hildesheim", "Hildesheim (Ger)").ratio()

print(sim)
