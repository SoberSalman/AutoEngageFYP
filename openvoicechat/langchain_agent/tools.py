from langchain.tools import BaseTool
from typing import Optional, Dict, Any, List

class ValidateZipcodeTool(BaseTool):
    name: str = "validate_zipcode"  # Add type annotation
    description: str = "Validates if a zipcode is valid and returns information about the area"  # Add type annotation
    
    def _run(self, zipcode: str) -> str:
        # In a real implementation, this would check a database or API
        # For now, just return a mock response
        return f"Zipcode {zipcode} is valid. It's in Los Angeles County, California."
    
    def _arun(self, zipcode: str) -> str:
        return self._run(zipcode)

class GetProductInfoTool(BaseTool):
    name: str = "get_product_info"  # Add type annotation
    description: str = "Gets detailed information about a specific product"  # Add type annotation
    
    def __init__(self, products: Dict[str, Dict[str, Any]]):
        """Initialize with product information."""
        super().__init__()
        self.products = products
    
    def _run(self, product_name: str) -> str:
        # Search for the product in the provided product dictionary
        for name, details in self.products.items():
            if product_name.lower() in name.lower():
                return f"{name}: {details.get('description', '')} {details.get('feature', '')}"
        return "Product information not found."
    
    def _arun(self, product_name: str) -> str:
        return self._run(product_name)

class UpdateNameTool(BaseTool):
    name: str = "update_name"
    description: str = "Updates the user's name"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, name: str) -> str:
        self.user_info_instance.name = name
        return f"Updated user name to {name}"
    
    def _arun(self, name: str) -> str:
        return self._run(name)

class UpdateAgeTool(BaseTool):
    name: str = "update_age"
    description: str = "Updates the user's age"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, age: str) -> str:
        try:
            self.user_info_instance.age = int(age)
            return f"Updated user age to {age}"
        except ValueError:
            return f"Could not update age: {age} is not a valid number"
    
    def _arun(self, age: str) -> str:
        return self._run(age)

class UpdateCityTool(BaseTool):
    name: str = "update_city"
    description: str = "Updates the user's city"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, city: str) -> str:
        self.user_info_instance.city = city
        return f"Updated user city to {city}"
    
    def _arun(self, city: str) -> str:
        return self._run(city)

class UpdateZipcodeTool(BaseTool):
    name: str = "update_zipcode"
    description: str = "Updates the user's zipcode"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, zipcode: str) -> str:
        self.user_info_instance.zipcode = zipcode
        return f"Updated user zipcode to {zipcode}"
    
    def _arun(self, zipcode: str) -> str:
        return self._run(zipcode)

class UpdateInterestTool(BaseTool):
    name: str = "update_interest"
    description: str = "Updates the user's interest level"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, interest: str) -> str:
        if "yes" in interest.lower() or "interested" in interest.lower():
            self.user_info_instance.interest_level = "Interested"
        elif "no" in interest.lower() or "not" in interest.lower():
            self.user_info_instance.interest_level = "Not interested"
        else:
            self.user_info_instance.interest_level = "Maybe interested"
        return f"Updated user interest to {self.user_info_instance.interest_level}"
    
    def _arun(self, interest: str) -> str:
        return self._run(interest)

class VerifyInfoTool(BaseTool):
    name: str = "verify_info"
    description: str = "Marks a field as verified"

    def __init__(self, user_info_instance):
        super().__init__()
        self.user_info_instance = user_info_instance

    def _run(self, field: str) -> str:
        if field == "name":
            self.user_info_instance.verified['name'] = True
        elif field == "age":
            self.user_info_instance.verified['age'] = True
        elif field == "city":
            self.user_info_instance.verified['city'] = True
        elif field == "zipcode":
            self.user_info_instance.verified['zipcode'] = True
        elif field == "interest":
            self.user_info_instance.verified['interest'] = True
        return f"Verified user {field}"
    
    def _arun(self, field: str) -> str:
        return self._run(field)

def create_user_info_tools(user_info_instance):
    """Create tools that interact with the UserInformation instance."""
    return [
        UpdateNameTool(user_info_instance),
        UpdateAgeTool(user_info_instance),
        UpdateCityTool(user_info_instance),
        UpdateZipcodeTool(user_info_instance),
        UpdateInterestTool(user_info_instance),
        VerifyInfoTool(user_info_instance),
    ]