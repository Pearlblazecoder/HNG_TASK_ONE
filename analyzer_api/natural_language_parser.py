import re
from django.db.models import Q

class NaturalLanguageQueryParser:
    """
    Natural language query parser for string analysis filters
    """
    
    @staticmethod
    def parse(query):
        """
        Parse natural language query and return Django Q filters
        Returns: Q object for filtering
        Raises: ValueError if query cannot be parsed
        """
        query = query.lower().strip()
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        filters = Q()
        parsed_filters = {}
    
        palindrome_filters = NaturalLanguageQueryParser._parse_palindrome(query)
        if palindrome_filters:
            filters &= palindrome_filters
            parsed_filters['is_palindrome'] = True
        
        length_filters = NaturalLanguageQueryParser._parse_length(query)
        if length_filters:
            filters &= length_filters
            if hasattr(length_filters, 'children'):
                for field, value in length_filters.children:
                    if 'length__gt' in str(field):
                        parsed_filters['min_length'] = value + 1
                    elif 'length__gte' in str(field):
                        parsed_filters['min_length'] = value
        
        word_filters = NaturalLanguageQueryParser._parse_word_count(query)
        if word_filters:
            filters &= word_filters
            if hasattr(word_filters, 'children'):
                for field, value in word_filters.children:
                    if 'word_count' in str(field):
                        parsed_filters['word_count'] = value
    
        char_filters = NaturalLanguageQueryParser._parse_contains_character(query)
        if char_filters:
            filters &= char_filters
            if hasattr(char_filters, 'children'):
                for field, value in char_filters.children:
                    if 'value__icontains' in str(field):
                        parsed_filters['contains_character'] = value
        
        return filters, parsed_filters
    
    @staticmethod
    def _parse_palindrome(query):
        """Parse palindrome-related queries"""
        palindrome_terms = [
            'palindrome', 'palindromic', 'same forwards and backwards', 
            'reads the same', 'symmetrical', 'mirror'
        ]
        
        if any(term in query for term in palindrome_terms):
            if any(negation in query for negation in ['not', 'non', 'no ']):
                return Q(is_palindrome=False)
            else:
                return Q(is_palindrome=True)
        return None
    
    @staticmethod
    def _parse_length(query):
        """Parse length-related queries"""
        numbers = re.findall(r'\b\d+\b', query)
        
        if not numbers:
            return None
        
        number = int(numbers[0])
        if any(term in query for term in ['longer than', 'more than', 'greater than', 'over']):
            return Q(length__gt=number)
        if any(term in query for term in ['shorter than', 'less than', 'under']):
            return Q(length__lt=number)
        if any(term in query for term in ['at least', 'minimum', 'min']):
            return Q(length__gte=number)
        if any(term in query for term in ['at most', 'maximum', 'max']):
            return Q(length__lte=number)
        if 'character' in query and len(numbers) == 1:
            return Q(length=number)
        
        return None
    
    @staticmethod
    def _parse_word_count(query):
        """Parse word count related queries"""
        if any(term in query for term in ['single word', 'one word']):
            return Q(word_count=1)
        if any(term in query for term in ['multiple words', 'multi word', 'more than one word']):
            return Q(word_count__gt=1)
        if any(term in query for term in ['no words', 'zero words', 'empty string']):
            return Q(word_count=0)
        word_count_map = {
            'two words': 2, 'three words': 3, 'four words': 4, 'five words': 5
        }
        
        for term, count in word_count_map.items():
            if term in query:
                return Q(word_count=count)
        numbers = re.findall(r'\b\d+\b', query)
        if numbers and 'word' in query:
            return Q(word_count=int(numbers[0]))
        
        return None
    
    @staticmethod
    def _parse_contains_character(query):
        """Parse contains character queries"""
        char_patterns = [
            r'containing\s+[\'"]?([a-zA-Z])[\'"]?',
            r'with\s+[\'"]?([a-zA-Z])[\'"]?',
            r'has\s+[\'"]?([a-zA-Z])[\'"]?',
            r'containing\s+the\s+letter\s+([a-zA-Z])',
            r'with\s+the\s+letter\s+([a-zA-Z])',
            r'has\s+the\s+letter\s+([a-zA-Z])'
        ]
        
        for pattern in char_patterns:
            match = re.search(pattern, query)
            if match:
                char = match.group(1).lower()
                return Q(value__icontains=char)
        char_aliases = {
            'first vowel': 'a',
            'vowel a': 'a', 'vowel e': 'e', 'vowel i': 'i', 'vowel o': 'o', 'vowel u': 'u',
            'letter a': 'a', 'letter b': 'b', 'letter c': 'c', 'letter z': 'z'
        }
        
        for alias, char in char_aliases.items():
            if alias in query:
                return Q(value__icontains=char)
        
        return None