from enum import Enum

class MutationType(Enum, str):
    SWAP = "Обмен генов"
    RANDOM_RESET = "Замена генов"