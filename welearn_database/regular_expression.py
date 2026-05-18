# Regular expressions for data cleaning and preprocessing in the WeLearn Database project.

# description: Matches backline characters (newline, tab, carriage return) for removal or replacement.
# example: "Hello\n\tWorld" -> matches "\n" and "\t"
# limit: Does not match other whitespace characters like spaces or form feeds.
BACKLINES_REGEX = r"([\n\t\r])"

# description: Match DOI identifier without doi.org as prefix
# example : 10.1590/s0103-90162002000200027 -> matches "10.1590/s0103-90162002000200027"
# limit : can't be really used for extraction, can be roughly used for other things than validation
DOI_VALIDATION_REGEX = r"^(10\.\d{4,5}\/[\S]+[^;,.\s])$"
