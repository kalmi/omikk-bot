from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

def validate(x):
  try:
    EmailValidator().__call__(x)
    return True
  except ValidationError: 
    return False
