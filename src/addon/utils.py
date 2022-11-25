
# if by is negative, lightens color
def darken(hex: str, by: int) -> str:
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    r = r + by
    g = g + by
    b = b + by
    r = max(0, min(16**2 - 1, r))
    g = max(0, min(16**2 - 1, g))
    b = max(0, min(16**2 - 1, b))
    hex[1:3] = "%0.2X" % r
    hex[3:5] = "%0.2X" % g
    hex[5:7] = "%0.2X" % b
