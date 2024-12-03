from typing import Any
import re
import random, string

#TODO IndexError: string index out of range 
# CAN'T EXCLUDE EVERYNUMBER OR IT BREAKS.

class PasswordFactory:
    @staticmethod
    def _get_chars(exclude_chars:list=None)->dict:
        """ 
       _get_chars()
        Params:
            exclude_chars: list - default None. used to exclude certain chars from the password. e.g., ['*','<','>','&']
        Calls: N/A
        Returns: dict of chars for use in password
        Description: 
            receives list of chars to exclude, gets all character types to be used in password generation.
            returns dict of uppercase, lowercase, digits, punctuation and all chars combined.
        """
        # Define the character sets
        uppercase_chars = string.ascii_uppercase
        lowercase_chars = string.ascii_lowercase
        digit_chars = string.digits
        punctuation_chars = string.punctuation

        # Exclude characters if specified
        if exclude_chars:
            uppercase_chars = ''.join(char for char in uppercase_chars if char not in exclude_chars)
            lowercase_chars = ''.join(char for char in lowercase_chars if char not in exclude_chars)
            digit_chars = ''.join(char for char in digit_chars if char not in exclude_chars)
            punctuation_chars = ''.join(char for char in punctuation_chars if char not in exclude_chars)
        
        chars = {
            "uppercase_chars":uppercase_chars, 
            "lowercase_chars":lowercase_chars,
            "digit_chars":digit_chars,
            "punctuation_chars":punctuation_chars,
            "all_chars":(uppercase_chars + lowercase_chars + digit_chars + punctuation_chars)
                }
        return chars
    
    @staticmethod
    def _get_random_char_lengths(min_length:int=4, max_length:int=20)->dict:
        """ 
        Params:
            min_length: int - default 4. used to set minimum length for a password
            max_length: int - default 20. used to set maximum length for a password
        Calls: N/A
        Returns: dict of random ints related to a char type
        Description: 
            receives min and max length, generates random ints for each char type ensuring that 1 of each type will always be present.
            returns dict of random ints for each type to be used to generate the password string.
        """
        # Ensure min_length and max_length are within bounds
        min_length = max(4, min_length)
        max_length = max(min_length, max_length)
        
        length_uppercase=max(1, min(random.randint(1, max_length - 3), max_length - 3))
        length_lowercase=max(1, min(random.randint(1, max_length - length_uppercase - 2), max_length - length_uppercase - 2))
        length_digits=max(1, min(random.randint(1, max_length - length_uppercase - length_lowercase - 1), max_length - length_uppercase - length_lowercase - 1))
        
        char_lengths = {
            "length_uppercase":length_uppercase,
            "length_lowercase":length_lowercase,
            "length_digits":length_digits,
            "length_punctuation":max_length - length_uppercase - length_lowercase - length_digits,
            "max_length":max_length
        }
        return char_lengths
    
    @staticmethod
    def validate_exclude_chars(exclude_chars:Any):
        if isinstance(exclude_chars, str):
            exclude_chars.strip().replace(' ', '')
            return list(set(exclude_chars))
        elif isinstance(exclude_chars, list):
            return list(set(exclude_chars))
        elif isinstance(exclude_chars, (int, float, complex)):
            return list(set(str(exclude_chars))) # maybe they just want to exclude numbers?
        else:
            raise AttributeError(f"Exclude Chars appears to be a invalid format. expected list or string. received {type(exclude_chars)}")

    @staticmethod
    def generate_password(min_length:int=4, max_length:int=20, exclude_chars:Any=None):
        """ 
        Params:
            min_length: int - default 4. used to set minimum length for a password
            max_length: int - default 20. used to set maximum length for a password
            exclude_chars: list - default None. used to exclude certain chars from the password. e.g., ['*','<','>','&']
        Calls: N/A
        Returns: new password
        Description: 
            Generates a random password. Will always return atleast 1 uppercase, 1 lowercase, 1 digit and 1 special char in each password.
            User can toggle min length above 4 and any max length. You can pass in a list of characters, digits or punctuation to exclude from the password.
        """
        if exclude_chars:
            exclude_chars = PasswordFactory.validate_exclude_chars(exclude_chars)
        all_chars = PasswordFactory._get_chars(exclude_chars=exclude_chars)
        char_lengths = PasswordFactory._get_random_char_lengths(min_length=int(min_length), max_length=int(max_length))

        # Generate password using the specified lengths for each character set
        password = (
            ''.join(random.choices(all_chars.get('uppercase_chars'), k=char_lengths.get('length_uppercase'))) +
            ''.join(random.choices(all_chars.get('lowercase_chars'), k=char_lengths.get('length_lowercase'))) +
            ''.join(random.choices(all_chars.get('digit_chars'), k=char_lengths.get('length_digits'))) +
            ''.join(random.choices(all_chars.get('punctuation_chars'), k=char_lengths.get('length_punctuation')))
        )
        # Fill the remaining characters with a random selection from all allowed characters
        remaining_length = char_lengths.get('max_length') - len(password)
        password += ''.join(random.choices(all_chars.get('all_chars'), k=remaining_length))

        # Shuffle the password to randomize the order of characters
        password_list = list(password)
        random.shuffle(password_list)
        new_password =  ''.join(password_list)
        return new_password