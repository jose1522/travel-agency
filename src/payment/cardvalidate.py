import re


def sum_digits(n):
    r = 0
    while n:
        r, n = r + n % 10, n // 10
    return r


# Validate card number using Luhn's checksum algorithm
def check_card_number(card_number):
    # Get card number as list of digits
    card_number_list = list(map(int, list(card_number.replace(" ", ""))))
    # Split digit list into odd-indexed and even-indexed lists
    odd_card_number = card_number_list[1::2]
    even_card_number = [sum_digits(digit * 2) for digit in card_number_list[::2]]
    checksum = sum([x + y for x, y in zip(odd_card_number, even_card_number)])
    return checksum % 2 == 0


# Identify card issuer based on card number regex
def check_issuer(card_number):
    card_number = card_number.replace(" ", "")
    issuer_dict = {"Amex": "^3[47][0-9]{13}$",
                   "BCGlobal": "^(6541|6556)[0-9]{12}$",
                   "Carte Blanche": "^389[0-9]{11}$",
                   "Diners Club": "^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
                   "Discover": "^65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(?:12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})$",
                   "Insta Payment": "^63[7-9][0-9]{13}$",
                   "JCB": "^(?:2131|1800|35\d{3})\d{11}$",
                   "KoreanLocal:": " ^9[0-9]{15}$",
                   "Laser": "^(6304|6706|6709|6771)[0-9]{12,15}$",
                   "Maestro": "^(5018|5020|5038|6304|6759|6761|6763)[0-9]{8,15}$",
                   # "Mastercard": "^5[1-5][0-9]{14}$}",
                   "Solo": "^(6334|6767)[0-9]{12}|(6334|6767)[0-9]{14}|(6334|6767)[0-9]{15}$",
                   "Switch": "^(4903|4905|4911|4936|6333|6759)[0-9]{12}|(4903|4905|4911|4936|6333|6759)[0-9]{14}|(4903|4905|4911|4936|6333|6759)[0-9]{15}|564182[0-9]{10}|564182[0-9]{12}|564182[0-9]{13}|633110[0-9]{10}|633110[0-9]{12}|633110[0-9]{13}$",
                   "Union Pay": "^(62[0-9]{14,17})$",
                   "Visa": "^4[0-9]{12}(?:[0-9]{3})?$",
                   "Mastercard": "^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})$"
                   }
    for card, regex in issuer_dict.items():
        if re.search(regex, card_number):
            return card


def check_cvv(card_cvv, card_issuer):
    if card_issuer == 'Maestro':
        return True
    elif card_issuer == 'Amex':
        return len(card_cvv) == 4
    else:
        return len(card_cvv) == 3