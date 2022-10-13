from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import Literal, Optional

from phdi.fhir.harmonization.standardization import standardize_names
from phdi.fhir.harmonization.standardization import standardize_phones

api = FastAPI()

def check_for_fhir(value: dict) -> dict:
    """
    Check to see if the value provided for 'data' is a FHIR resource or bundle.
    """

    assert (
        value.get("resourceType") != None
    ), "Must provide a FHIR resource or bundle"
    return value

class StandardizeNamesInput(BaseModel):
    data: dict
    trim: Optional[bool] = True
    overwrite: Optional[bool] = True
    case: Optional[Literal["upper", "lower", "title"]] = "upper"
    remove_numbers: Optional[bool] = True

    _check_for_fhir = validator('data', allow_reuse=True)(check_for_fhir)


class StandardizePhonesInput(BaseModel):
    data: dict
    overwrite: Optional[bool] = True

    _check_for_fhir = validator('data', allow_reuse=True)(check_for_fhir)


@api.get("/")
async def health_check() -> dict:
    return {"status": "OK"}

@api.post("/standardize_names")
async def standardize_names(input: StandardizeNamesInput) -> dict:
    """
    Standardize the names in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizeNamesInput 
        model.
    :return: A FHIR bundle or resource with standardized names.
    """
    input = dict(input)
    return standardize_names(**input)


@api.post("/standardize_phones")
async def standardize_phones(input: StandardizePhonesInput) -> dict:
    """
    Standardize the phone numbers in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizePhonesInput 
        model.
    :return: A FHIR bundle with standardized phone numbers.
    """
    input = dict(input)
    return standardize_phones(**input)
