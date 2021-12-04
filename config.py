DATA_DIR = r"C:\Users\rrm2308\data\tmr-empathy"

CONDITION_MAP = {
    1: "mw",
    2: "bct",
    3: "mw",
    4: "bct"
}

def no_leading_zeros(x, pos):
    # a custom tick formatter for matplotlib
    # to show decimals without a leading zero
    val_str = "{:g}".format(x)
    if abs(x) > 0 and abs(x) < 1:
        return val_str.replace("0", "", 1)
    else:
        return val_str