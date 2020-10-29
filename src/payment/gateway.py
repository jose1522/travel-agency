import random
from api.validation import Transaction, CreditCard
from api.messages import Message
import payment.cardvalidate as cc
from datetime import datetime


class Verification(Message):

    def __init__(self, transaction: Transaction):
        super().__init__()
        self.transaction = transaction
        self.__today = datetime.today()
        self.__thisMonth = self.__today.month
        self.__thisYear = self.__today.year

    def verifyCard(self):
        result: bool
        try:
            result =    self.__verifyNumber() and \
                        self.__verifyDate() and \
                        self.__verifyIssuer() and \
                        self.__verifyCVV()
        except:
            result = False
        finally:
            return result

    def __verifyNumber(self):
        result: bool
        try:
            result = cc.check_card_number(str(self.transaction.number))
        except Exception as e:
            result = False
        finally:
            if not result:
                self.addMessage('-1', 'Invalid card number')
            return result

    def __verifyDate(self):
        result: bool
        try:
            month = self.transaction.month
            year = self.transaction.year
            result = month in range(1, 12) and \
                     month >= self.__thisMonth and \
                     year >= self.__thisYear
        except:
            result = False
        finally:
            if not result:
                self.addMessage('-2', 'Invalid or expired date')
            return result

    def __verifyCVV(self):
        issuer = self.transaction.issuer
        cvv = str(self.transaction.cvv)
        result: bool
        try:
            result = cc.check_cvv(cvv, issuer)
        except Exception as e:
            result = False
        finally:
            if not result:
                self.addMessage('-3', 'Invalid CVV')
            return result

    def __verifyIssuer(self):
        ccNumber = str(self.transaction.number)
        issuer = self.transaction.issuer
        result: bool
        try:
            result = cc.check_issuer(ccNumber).upper() == issuer.upper()
        except Exception as e:
            result = False
        finally:
            if not result:
                self.addMessage('-4', 'Invalid Issuer')
            return result


class Authorization(Message):

    def __init__(self, transaction: Transaction):
        super().__init__()
        self.transaction = transaction

    def processTransaction(self):
        result = self.__authorizeAmount()
        if result:
            self.addMessage('0',  'Successful transaction')
        return result

    def __authorizeAmount(self):
        if self.transaction.card_type.upper() == 'DEBIT':
            result = bool(random.getrandbits(1))
        else:
            result = True
        if not result:
            self.addMessage('-5', 'Insufficient Funds')
        return result
