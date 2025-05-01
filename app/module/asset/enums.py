from enum import IntEnum, StrEnum


class AgeGroup(IntEnum):
    UNDER_20 = 1
    AGE_20_24 = 2
    AGE_25_29 = 3
    AGE_30_34 = 4
    AGE_35_39 = 5
    AGE_40_44 = 6
    AGE_45_49 = 7
    AGE_50_54 = 8
    AGE_55_59 = 9
    OVER_60 = 10


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
