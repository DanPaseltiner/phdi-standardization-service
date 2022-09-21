from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import Literal, Optional

from phdi.fhir.harmonization.standardization import standardize_names
from phdi.fhir.harmonization.standardization import standardize_phones

api = FastAPI()


class StandardizeNamesParameters(BaseModel):
    """
    Parameters for the standardize_names function.
    """

    trim: Optional[bool]
    overwrite: Optional[bool]
    case: Optional[Literal["upper", "lower", "title"]]
    remove_numbers: Optional[bool]


class StandardizePhonesParameters(BaseModel):
    """
    Parameters for the standardize_phones function.
    """

    overwrite: Optional[bool]


supported_standardizations = {
    "standardize_names": standardize_names,
    "standardize_phones": standardize_phones,
}

parameter_models = {
    "standardize_names": StandardizeNamesParameters,
    "standardize_phones": StandardizePhonesParameters,
}


class StandardizeInput(BaseModel):
    """
    Input parameters for the standardize endpoint.
    """

    data: dict
    standardizations: dict

    @validator("data")
    def check_for_fhir(cls: object, value: dict) -> dict:
        """
        Check to see if the value provided for 'data' is a FHIR resource or bundle.
        """

        assert (
            value.get("resourceType") != None
        ), "Must provide a FHIR resource or bundle"
        return value

    @validator("standardizations")
    def validate_parameters(cls: object, standardizations: dict) -> dict:
        """
        Ensure that proper parameters have been provided for requested standardizations.
        """

        for standardization, parameters in standardizations.items():
            assert standardization in supported_standardizations.keys(), (
                "Unsupported standardization requested. Currently supported",
                "standardizations include:",
                f"{', '.join(supported_standardizations.keys())}",
            )
            parameter_model = parameter_models[standardization]
            parameter_model(**parameters)

        return standardizations


class StandardizeNamesInput(BaseModel):
    data: dict
    trim: Optional[bool] = True
    overwrite: Optional[bool] = True
    case: Optional[Literal["upper", "lower", "title"]] = "upper"
    remove_numbers: Optional[bool] = True

    @validator("data")
    def check_for_fhir(cls: object, value: dict) -> dict:
        """
        Check to see if the value provided for 'data' is a FHIR resource or bundle.
        """

        assert (
            value.get("resourceType") != None
        ), "Must provide a FHIR resource or bundle"
        return value


class StandardizePhonesInput(BaseModel):
    data: dict
    overwrite: Optional[bool] = True

    @validator("data")
    def check_for_fhir(cls: object, value: dict) -> dict:
        """
        Check to see if the value provided for 'data' is a FHIR resource or bundle.
        """

        assert (
            value.get("resourceType") != None
        ), "Must provide a FHIR resource or bundle"
        return value


@api.post("/standardize")
async def standardize(input: StandardizeInput):
    """
    Apply the specified standardizations to the provided FHIR data.
    :param input: A JSON
    """
    input = dict(input)
    data = input["data"]
    for standardization, parameters in input["standardizations"].items():
        parameters["data"] = data
        data = supported_standardizations[standardization](**parameters)

    return data


@api.post("/standardize_names")
async def standardize_names_only(input: StandardizeNamesInput):
    """
    Standardize the names in the provided FHIR bundle or resource.
    """
    input = dict(input)
    return standardize_names(**input)


@api.post("/standardize_phones")
async def standardize_phones_only(input: StandardizePhonesInput):
    """
    Standardize the phone numbers in the provided FHIR bundle or resource.
    """
    input = dict(input)
    return standardize_phones(**input)
