# This composite survey consists of the Gold-standard weekly survey followed by
# the Gold-standard contact survey.

class GoldStandardCompositeWeekly(GoldStandardWeekly,GoldStandardContact):
    id = 'gold-standard-composite-weekly-0.1.0'
    rules = GoldStandardWeekly.rules + GoldStandardContact.rules
