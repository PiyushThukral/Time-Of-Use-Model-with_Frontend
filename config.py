# config.py

CONSUMER_PATTERNS = [
    "consumer",
    "cons_no",
    "cons no",
    "cons",
    "consumer_no",
    "consumer_number",
    "consumerid",
    "consumer id",
    "consumer_code",
]

STANDARD_CONSUMER_COLUMN = "Consumer No"

MONTH_CANDIDATES = ["month"]  # case-insensitive match

CATEGORY_PATTERNS = ["category", "category_code", "category code", "categorycode", "category_name"]

CONNECTED_LOAD_PATTERNS = [
    "connected_load",
    "connected load",
    "sanctioned_load_kw",
    "sanctioned load",
    "sanctioned_load",
    "sanctioned_load_(kw)",
    "sanctionedload(kw)"]

METER_NUMBER_PATTERNS = [
    "meter_no",
    "meter_number",
    "METER_NO",
    "Meter No",
    'Meter No',
    "METER_NUMBER",
    "MSN",
    "msn",
    "METER_SERIAL_NUMBER"
]

TIMEBLOCK_PATTERNS = {
    "TIMEBLOCK_PATTERNS": {
        "regex": [
            "ImportkWhTimeBlock\\d+",
            "Consumption_?Hr_\\d+",
            "ConsumptionHr\\d+"
        ],
        "prefix": [
            "importkwhtimeblock",
            "consumption_hr_",
            "consumptionhr"
        ]
    }
}
