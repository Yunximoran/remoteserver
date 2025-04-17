
def decimal_to_baseX(n, X):
    if n < 0:
        raise ValueError("")
    if n == 0:
        return [0]
    
    digits = []
    while n > 0:
        d = n % X
        n //= X
        digits.append(d)
    return digits[::-1]

def baseX_to_decimal(digits, X):
    num = 0
    for i, digit in enumerate(digits[::-1]):
        num += digit * (X ** i)
    return num

